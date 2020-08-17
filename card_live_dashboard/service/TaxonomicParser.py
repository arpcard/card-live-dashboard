import pandas as pd
from ete3 import NCBITaxa
import logging

logger = logging.getLogger(__name__)


class TaxonomicParser:

    def __init__(self, df_rgi_kmer: pd.DataFrame, df_lmat: pd.DataFrame):
        self._ncbi_taxa = NCBITaxa()

        self._df_rgi_kmer = df_rgi_kmer[['rgi_kmer.CARD*kmer Prediction']]
        self._df_lmat = df_lmat[['lmat.count', 'lmat.taxonomy_label', 'lmat.ncbi_taxon_id']].astype(
            {'lmat.count': 'float64'}
        )

        self._df_lmat = self.adjust_taxonomic_labels(self._df_lmat, 'lmat', min_rank='species')

        print(self._df_lmat[['lmat.ncbi_taxon_id', 'lmat.taxonomy_label', 'lmat.taxonomy_label_adjusted']])
        print(self._df_lmat['lmat.taxonomy_label_adjusted'].value_counts())

    def adjust_taxonomic_labels(self, df: pd.DataFrame, results_type: str, min_rank: str) -> pd.DataFrame:
        """
        Adjust the taxonomic identifiers and labels so that they don't fall below the specified minimum rank.
        :param df: The dataframe.
        :param results_type: The type of results to adjust (lmat or rgi kmer).
        :param min_rank: The minimum rank.
        :return: A new data frame with the additional columns.
        """
        if results_type == 'lmat':
            ncbi_id_col = 'lmat.ncbi_taxon_id'
            taxonomy_id_adj = 'lmat.ncbi_taxon_id_adjusted'
            taxonomy_label = 'lmat.taxonomy_label'
            taxonomy_label_adj = 'lmat.taxonomy_label_adjusted'
        else:
            raise Exception(f'Unknown type [type={results_type}]')

        df_new = df.reset_index()

        df_new[taxonomy_id_adj] = df_new[ncbi_id_col]
        df_new[taxonomy_id_adj] = df_new.loc[
            ~df_new[ncbi_id_col].isna(), ncbi_id_col].apply(
            self._limit_taxon_to, min_rank=min_rank)
        df_new[taxonomy_label_adj] = df_new[taxonomy_label]
        df_new[taxonomy_label_adj] = df_new.loc[~df_new[taxonomy_id_adj].isna(), taxonomy_id_adj].apply(
            lambda x: self._ncbi_taxa.get_taxid_translator([x]).get(x, pd.NA))

        return df_new.set_index('filename')

    def _limit_taxon_to(self, taxon_id: int, min_rank: str) -> int:
        """
        Given a taxonomic id and a rank limit the taxonomic id so that it is at the specified rank or higher.
        :param taxon_id: The taxonomic id.
        :param min_rank: The minimum limit for the rank (e.g., 'species', or 'family').
        :return: The taxonomic id that is at or above the passed min_rank, or the original id if the passed rank was
                 not found in the lineage.
        """
        taxon_id = int(taxon_id)
        try:
            lineages = self._ncbi_taxa.get_lineage(taxon_id)
            ranks = self._ncbi_taxa.get_rank(lineages)
            for lineage in lineages:
                if ranks[lineage] == min_rank:
                    return lineage
        except ValueError as e:
            logger.debug(f'Error when looking up lineage for taxon_id={taxon_id} in NCBI database.', e)

        return taxon_id

    def _create_contigs_lmat_score(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        df_sum = df['lmat.count'].groupby('filename').sum().rename('lmat_count_sum').to_frame()
        df_merged = df_sum.merge(df, how='left', on='filename')
        df_merged[name] = df_merged['lmat.count'] / df_merged['lmat_count_sum']

        return df_merged

    def create_filename_lmat_tax(self) -> pd.DataFrame:
        df_lmat_subset = self._create_contigs_lmat_score(self._df_lmat, 'lmat_real_score')
        df_lmat_subset = df_lmat_subset.sort_values(
            by=['filename', 'lmat_real_score', 'lmat.taxonomy_label'], ascending=False)
        df_lmat_subset = df_lmat_subset.groupby('filename').nth(0)

        return df_lmat_subset[['lmat.taxonomy_label']]

    def create_filename_rgi_kmer_tax(self) -> pd.DataFrame:
        df_tax = self._df_rgi_kmer.groupby('filename')['rgi_kmer.CARD*kmer Prediction'].apply(
            lambda x: x.replace(
                # Remove text like '(chromosome)'
                r' *\(.*\)', '', regex=True).value_counts()).reset_index()
        df_tax = df_tax.rename(columns={'level_1': 'rgi_kmer.taxonomy_label', 'rgi_kmer.CARD*kmer Prediction': 'rgi_kmer.prediction_count'})
        df_tax = df_tax.sort_values(by=['rgi_kmer.prediction_count', 'rgi_kmer.taxonomy_label'], ascending=False)
        df_tax = df_tax.groupby('filename').nth(0)['rgi_kmer.taxonomy_label']
        return df_tax.to_frame()

    def _matches_column(self, df: pd.DataFrame, left: str, right: str) -> pd.DataFrame:
        df_matches = df.copy()
        df_matches['matches'] = (df[left] == df[right])

        return df_matches

    def create_file_matches(self) -> pd.DataFrame:
        df_rgi = self.create_filename_rgi_kmer_tax()
        df_lmat = self.create_filename_lmat_tax()

        df_both = df_rgi.merge(df_lmat, on='filename', how='outer').fillna('N/A')
        df_both = self._matches_column(df_both, 'rgi_kmer.taxonomy_label', 'lmat.taxonomy_label')

        return df_both

    def create_rgi_lmat_both(self) -> pd.DataFrame:
        df_both = self.create_file_matches()

        df_both_counts = self._create_rgi_lmat_counts(df_both)
        df_rgi_unique = self.create_unique_counts(df_both, 'rgi_kmer.taxonomy_label', 'rgi_counts')
        df_lmat_unique = self.create_unique_counts(df_both, 'lmat.taxonomy_label', 'lmat_counts')

        df_count_all = df_both_counts.merge(
            df_rgi_unique, on='taxon', how='outer').merge(
            df_lmat_unique, on='taxon', how='outer').fillna(0)

        # Create a 'Total' column
        df_totals = df_count_all.sum(axis='columns').to_frame(name='Total')
        df_count_all = df_count_all.merge(df_totals, on='taxon')

        return df_count_all

    def _create_rgi_lmat_counts(self, df_both_matches: pd.DataFrame) -> pd.DataFrame:
        df_both_counts = df_both_matches[df_both_matches['matches']][
            'rgi_kmer.taxonomy_label'].value_counts().to_frame().rename(
            columns={'rgi_kmer.taxonomy_label': 'count_both'})
        df_both_counts.index.name = 'taxon'

        return df_both_counts

    def create_unique_counts(self, df_both_matches: pd.DataFrame, label: str, renamed_label: str) -> pd.DataFrame:
        df_counts = df_both_matches[~df_both_matches['matches']][label].value_counts().to_frame().rename(
            columns={label: renamed_label})
        df_counts.index.name = 'taxon'

        return df_counts
