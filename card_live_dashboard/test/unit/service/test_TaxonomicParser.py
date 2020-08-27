import pandas as pd
from unittest.mock import MagicMock

from card_live_dashboard.service.TaxonomicParser import TaxonomicParser




def test_taxonomic_parser_simple():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Salmonella enterica', '10'],
                               ['file1', 'Salmonella enterica', '10'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_no_match():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Salmonella enterica', '10'],
                               ['file1', 'Enterobacteriaceae', '20'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Enterobacteriaceae'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [False] == file_matches['matches'].tolist()


def test_taxonomic_parser_multiple_match():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Salmonella enterica', '20'],
                               ['file1', 'Enterobacteriaceae', '10'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_multiple_files():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Salmonella enterica', '20'],
                               ['file1', 'Enterobacteriaceae', '10'],
                               ['file2', 'Enterobacteriaceae', '20'],
                               ['file2', 'Salmonella enterica', '10'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (plasmid)'],
                                   ['file2', 'Enterobacteriaceae (chromosome)'],
                                   ['file2', 'Enterobacteriaceae (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 2 == len(file_matches)
    assert ['Salmonella enterica', 'Enterobacteriaceae'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Enterobacteriaceae', 'Enterobacteriaceae'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [False, True] == file_matches['matches'].tolist()


def test_taxonomic_parser_tie_case1():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Salmonella enterica', '20'],
                               ['file1', 'Enterobacteriaceae', '20'],
                               ['file1', 'Listeria monocytogenes', '10'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Listeria monocytogenes (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_tie_case2():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count'],
                           data=[
                               ['file1', 'Enterobacteriaceae', '20'],
                               ['file1', 'Listeria monocytogenes', '10'],
                               ['file1', 'Salmonella enterica', '20'],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Listeria monocytogenes (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()
