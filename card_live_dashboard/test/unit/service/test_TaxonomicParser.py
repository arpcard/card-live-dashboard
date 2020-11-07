from typing import List, Dict, Optional

import pandas as pd
from ete3 import NCBITaxa

from card_live_dashboard.service.TaxonomicParser import TaxonomicParser


# There's likely a way to use mock objects here instead of just creating a new class with the same methods
# as NCBITaxa, but I couldn't figure out how to do it. That is applying @unittest.mock.patch('ete3.NCBITaxa') wouldn't
# actually mock ete3.NCBITaxa.
# I also know there's a warning here that I'm not calling the superclass constructor, but I can't call it since it will
# attempt to install the entire NCBI Taxonomy database, which I don't want in unit tests.
class NCBITaxaMock(NCBITaxa):
    LINEAGES = {
        28901: 'Salmonella enterica',
        543: 'Enterobacteriaceae',
        1639: 'Listeria monocytogenes',
    }

    def __init__(self):
        pass

    def get_lineage(self, lineage: int) -> Optional[List[int]]:
        return [lineage]

    def get_rank(self, lineages: List[int]) -> Dict[int, str]:
        ranks = {}
        for lineage in lineages:
            ranks[lineage] = 'species'
        return ranks

    def get_taxid_translator(self, taxids: List[int], try_synonyms: bool = True) -> Dict[int, str]:
        names = {}
        for id in taxids:
            names[id] = self.LINEAGES[id]
        return names


def test_taxonomic_parser_simple():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Salmonella enterica', '10', 28901],
                               ['file1', 'Salmonella enterica', '10', 28901],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_no_match():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Salmonella enterica', '10', 28901],
                               ['file1', 'Enterobacteriaceae', '20', 543],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Enterobacteriaceae'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [False] == file_matches['matches'].tolist()


def test_taxonomic_parser_multiple_match():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Salmonella enterica', '20', 28901],
                               ['file1', 'Enterobacteriaceae', '10', 543],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_multiple_files():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Salmonella enterica', '20', 28901],
                               ['file1', 'Enterobacteriaceae', '10', 543],
                               ['file2', 'Enterobacteriaceae', '20', 543],
                               ['file2', 'Salmonella enterica', '10', 28901],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (plasmid)'],
                                   ['file2', 'Enterobacteriaceae (chromosome)'],
                                   ['file2', 'Enterobacteriaceae (plasmid)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 2 == len(file_matches)
    assert ['Salmonella enterica', 'Enterobacteriaceae'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Enterobacteriaceae', 'Enterobacteriaceae'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [False, True] == file_matches['matches'].tolist()


def test_taxonomic_parser_tie_case1():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Salmonella enterica', '20', 28901],
                               ['file1', 'Enterobacteriaceae', '20', 543],
                               ['file1', 'Listeria monocytogenes', '10', 1639],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Listeria monocytogenes (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()


def test_taxonomic_parser_tie_case2():
    lmat_df = pd.DataFrame(columns=['filename', 'lmat.taxonomy_label', 'lmat.count', 'lmat.ncbi_taxon_id'],
                           data=[
                               ['file1', 'Enterobacteriaceae', '20', 543],
                               ['file1', 'Listeria monocytogenes', '10', 1639],
                               ['file1', 'Salmonella enterica', '20', 28901],
                           ]).set_index('filename')

    rgi_kmer_df = pd.DataFrame(columns=['filename', 'rgi_kmer.CARD*kmer Prediction'],
                               data=[
                                   ['file1', 'Listeria monocytogenes (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Salmonella enterica (chromosome)'],
                                   ['file1', 'Enterobacteriaceae (chromosome)'],
                               ]).set_index('filename')

    tax = TaxonomicParser(ncbi_taxa=NCBITaxaMock(), df_lmat=lmat_df, df_rgi_kmer=rgi_kmer_df)
    file_matches = tax.create_file_matches()

    assert 1 == len(file_matches)
    assert ['Salmonella enterica'] == file_matches['lmat.taxonomy_label'].tolist()
    assert ['Salmonella enterica'] == file_matches['rgi_kmer.taxonomy_label'].tolist()
    assert [True] == file_matches['matches'].tolist()
