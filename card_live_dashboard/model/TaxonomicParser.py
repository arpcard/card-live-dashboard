import pandas as pd
import geopandas
import numpy as np
import json
from os import path
from pathlib import Path
from flatten_json import flatten

class TaxonomicParser:

    def __init__(self, df_rgi_kmer, df_lmat):
        self._df_rgi_kmer = df_rgi_kmer[['rgi_kmer.CARD*kmer Prediction',
                                         'rgi_kmer.Taxonomic kmers',
                                         'rgi_kmer.Genomic kmers',
                                         'rgi_version']]

        self._df_lmat = df_lmat[['lmat.score',
                                 'lmat.count',
                                 'lmat.ncbi_taxon_id',
                                 'lmat.rank',
                                 'lmat.taxonomy_label',
                                 'lmat_version']].astype(
            {'lmat.score': 'float64',
             'lmat.count': 'float64'}
        )

    def create_contigs_lmat_score(self, df, name):
        df_sum = df['lmat.count'].groupby('filename').sum().rename('lmat_count_sum').to_frame()
        df_merged = df_sum.merge(df, how='left', on='filename')
        df_merged[name] = df_merged['lmat.count'] / df_merged['lmat_count_sum']

        return df_merged

    def create_filename_lmat_tax(self):
        df_lmat_subset = self.create_contigs_lmat_score(self._df_lmat, 'lmat_real_score')
        df_lmat_subset = df_lmat_subset.sort_values(by=['filename', 'lmat_real_score'], ascending=False).groupby(
            'filename').nth(0)

        return df_lmat_subset[['lmat.taxonomy_label']]

    def create_filename_rgi_kmer_tax(self):
        df_tax = self._df_rgi_kmer.groupby('filename')['rgi_kmer.CARD*kmer Prediction'].apply(
            lambda x: x.replace(
                # Remove text like '(chromosome)'
                ' *\(.*\)', '', regex=True).value_counts(
                sort=True, ascending=False)).reset_index()
        df_tax = df_tax.groupby('filename').nth(0)
        df_tax = df_tax.rename(columns={'level_1': 'rgi_kmer.taxonomy_label'})['rgi_kmer.taxonomy_label']
        return df_tax.to_frame()

    def matches_column(self, df, left, right):
        df_matches = df.copy()
        df_matches['matches'] = (df[left] == df[right])

        return df_matches

    def create_file_matches(self):
        df_rgi = self.create_filename_rgi_kmer_tax()
        df_lmat = self.create_filename_lmat_tax()

        df_both = df_rgi.merge(df_lmat, on='filename', how='outer').fillna('N/A')
        df_both = self.matches_column(df_both, 'rgi_kmer.taxonomy_label', 'lmat.taxonomy_label')

        return df_both

    def create_rgi_lmat_both(self):
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

    def create_rgi_lmat_counts(self, df_both_matches):
        df_both_counts = df_both_matches[df_both_matches['matches']][
            'rgi_kmer.taxonomy_label'].value_counts().to_frame().rename(
            columns={'rgi_kmer.taxonomy_label': 'count_both'})
        df_both_counts.index.name = 'taxon'

        return df_both_counts

    def create_unique_counts(self, df_both_matches, label, renamed_label):
        df_counts = df_both_matches[~df_both_matches['matches']][label].value_counts().to_frame().rename(
            columns={label: renamed_label})
        df_counts.index.name = 'taxon'

        return df_counts