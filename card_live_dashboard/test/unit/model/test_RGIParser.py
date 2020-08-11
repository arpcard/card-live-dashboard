import pandas as pd

from card_live_dashboard.model.RGIParser import RGIParser

RGI_DF = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', 'Perfect', 'class1; class2', 'gene1'],
          ['file1', 'Strict', 'class1; class2; class3', 'gene2'],
          ['file2', 'Perfect', 'class1; class2; class4', 'gene1'],
          ['file3', None, None, None],
          ]
).set_index('filename')
RGI_PARSER = RGIParser(RGI_DF)

RGI_DF_NONE = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', None, '', None],
          ['file2', None, None, None]
          ]
).set_index('filename')
RGI_PARSER_NONE = RGIParser(RGI_DF_NONE)

RGI_DF_NA = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', None, '', pd.NA],
          ['file2', None, pd.NA, pd.NA]
          ]
).set_index('filename')
RGI_PARSER_NA = RGIParser(RGI_DF_NA)


def test_all_drugs():
    assert {'class1', 'class2', 'class3', 'class4'} == RGI_PARSER.all_drugs()


def test_all_drugs_only_none():
    assert set() == RGI_PARSER_NONE.all_drugs()


def test_all_drugs_only_na():
    assert set() == RGI_PARSER_NA.all_drugs()


def test_all_drugs_empty():
    rgi_df_empty = pd.DataFrame(
        columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
        data=[]
    ).set_index('filename')
    rgi_parser_empty = RGIParser(rgi_df_empty)
    assert set() == rgi_parser_empty.all_drugs()


def test_all_besthit_aro():
    assert {'gene1', 'gene2'} == RGI_PARSER.all_besthit_aro()


def test_all_besthit_aro_only_none():
    assert set() == RGI_PARSER_NONE.all_besthit_aro()


def test_all_besthit_aro_only_na():
    assert set() == RGI_PARSER_NA.all_besthit_aro()
