import pandas as pd


class TaxonomicParser:

    def __init__(self, df_rgi_kmer: pd.DataFrame, df_lmat: pd.DataFrame):
        self._df_rgi_kmer = df_rgi_kmer[['rgi_kmer.CARD*kmer Prediction']]

        self._df_lmat = df_lmat[['lmat.count', 'lmat.taxonomy_label']].astype(
            {'lmat.count': 'float64'}
        )

    def create_contigs_lmat_score(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        df_sum = df['lmat.count'].groupby('filename').sum().rename('lmat_count_sum').to_frame()
        df_merged = df_sum.merge(df, how='left', on='filename')
        df_merged[name] = df_merged['lmat.count'] / df_merged['lmat_count_sum']

        return df_merged

    def create_filename_lmat_tax(self) -> pd.DataFrame:
        df_lmat_subset = self.create_contigs_lmat_score(self._df_lmat, 'lmat_real_score')
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

    def matches_column(self, df: pd.DataFrame, left: str, right: str) -> pd.DataFrame:
        df_matches = df.copy()
        df_matches['matches'] = (df[left] == df[right])

        return df_matches

    def create_file_matches(self) -> pd.DataFrame:
        df_rgi = self.create_filename_rgi_kmer_tax()
        df_lmat = self.create_filename_lmat_tax()

        df_both = df_rgi.merge(df_lmat, on='filename', how='outer').fillna('N/A')
        df_both = self.matches_column(df_both, 'rgi_kmer.taxonomy_label', 'lmat.taxonomy_label')

        return df_both

    def create_rgi_lmat_both(self) -> pd.DataFrame:
        df_both = self.create_file_matches()

        df_both_counts = self.create_rgi_lmat_counts(df_both)
        df_rgi_unique = self.create_unique_counts(df_both, 'rgi_kmer.taxonomy_label', 'rgi_counts')
        df_lmat_unique = self.create_unique_counts(df_both, 'lmat.taxonomy_label', 'lmat_counts')

        df_count_all = df_both_counts.merge(
            df_rgi_unique, on='taxon', how='outer').merge(
            df_lmat_unique, on='taxon', how='outer').fillna(0)

        # Create a 'Total' column
        df_totals = df_count_all.sum(axis='columns').to_frame(name='Total')
        df_count_all = df_count_all.merge(df_totals, on='taxon')

        return df_count_all

    def create_rgi_lmat_counts(self, df_both_matches: pd.DataFrame) -> pd.DataFrame:
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
