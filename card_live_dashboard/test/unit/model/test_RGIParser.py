import numpy as np
import pandas as pd

from card_live_dashboard.model.RGIParser import RGIParser

RGI_DF = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', 'Perfect', 'class1; class2', 'gene1'],
          ['file1', 'Strict', 'class1; class2; class3', 'gene2'],
          ['file2', 'Perfect', 'class1; class2; class4', 'gene1'],
          ['file2', 'Perfect', 'class5', 'gene1'],
          ['file2', 'Perfect', '', 'gene1'],
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

RGI_DF_ONLY_EMPTY_STRING = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', None, '', pd.NA],
          ['file2', None, '', pd.NA]
          ]
).set_index('filename')
RGI_PARSER_ONLY_EMPTY_STRING = RGIParser(RGI_DF_ONLY_EMPTY_STRING)

RGI_DF_ONLY_NA = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', None, pd.NA, pd.NA],
          ['file2', None, np.nan, pd.NA]
          ]
).set_index('filename')
RGI_PARSER_ONLY_NA = RGIParser(RGI_DF_ONLY_NA)

RGI_DF_ONLY_NUMPY_NAN = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', np.nan, np.nan, np.nan],
          ['file2', np.nan, np.nan, np.nan]
          ]
).set_index('filename')
RGI_PARSER_ONLY_NUMPY_NAN = RGIParser(RGI_DF_ONLY_NUMPY_NAN)


def test_all_drugs():
    assert {'class1', 'class2', 'class3', 'class4', 'class5'} == RGI_PARSER.all_drugs()


def test_all_drugs_only_none():
    assert set() == RGI_PARSER_NONE.all_drugs()


def test_all_drugs_only_na():
    assert set() == RGI_PARSER_NA.all_drugs()


def test_all_drugs_only_empty_string():
    assert set() == RGI_PARSER_ONLY_EMPTY_STRING.all_drugs()


def test_all_drugs_only_na_values():
    assert set() == RGI_PARSER_ONLY_NA.all_drugs()


def test_all_drugs_empty():
    rgi_df_empty = pd.DataFrame(
        columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
        data=[]
    ).set_index('filename')
    rgi_parser_empty = RGIParser(rgi_df_empty)
    assert set() == rgi_parser_empty.all_drugs()


def test_all_amr_genes():
    assert {'gene1', 'gene2'} == RGI_PARSER.all_amr_genes()


def test_all_amr_genes_only_none():
    assert set() == RGI_PARSER_NONE.all_amr_genes()


def test_all_amr_genes_only_na():
    assert set() == RGI_PARSER_NA.all_amr_genes()


def test_expand_drug_class():
    expanded_df = RGI_PARSER.explode_column('rgi_main.Drug Class')
    assert 11 == len(expanded_df)
    assert ['file1', 'file1', 'file1', 'file1', 'file1',
            'file2', 'file2', 'file2', 'file2', 'file2', 'file3'] == expanded_df.index.tolist()

    value_counts = expanded_df['rgi_main.Drug Class'].groupby('filename').value_counts()
    assert 2 == value_counts['file1']['class1; class2']
    assert 3 == value_counts['file1']['class1; class2; class3']
    assert 3 == value_counts['file2']['class1; class2; class4']
    assert 1 == value_counts['file2']['class5']
    assert 'file3' not in value_counts

    assert ['class1', 'class2', 'class1', 'class2', 'class3',
            'class1', 'class2', 'class4', 'class5'] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file3', 'rgi_main.Drug Class_exploded'])


def test_expand_drug_class_none():
    expanded_df = RGI_PARSER_NONE.explode_column('rgi_main.Drug Class')
    assert 2 == len(expanded_df)
    assert ['file1', 'file2'] == expanded_df.index.tolist()

    assert '' == expanded_df.loc['file1', 'rgi_main.Drug Class']

    assert [] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class_exploded'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class_exploded'])


def test_expand_drug_class_na():
    expanded_df = RGI_PARSER_NA.explode_column('rgi_main.Drug Class')
    assert 2 == len(expanded_df)
    assert ['file1', 'file2'] == expanded_df.index.tolist()

    assert '' == expanded_df.loc['file1', 'rgi_main.Drug Class']
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class'])

    assert [] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class_exploded'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class_exploded'])


def test_expand_drug_class_only_empty_string():
    expanded_df = RGI_PARSER_ONLY_EMPTY_STRING.explode_column('rgi_main.Drug Class')
    assert 2 == len(expanded_df)
    assert ['file1', 'file2'] == expanded_df.index.tolist()

    assert '' == expanded_df.loc['file1', 'rgi_main.Drug Class']
    assert '' == expanded_df.loc['file2', 'rgi_main.Drug Class']

    assert [] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class_exploded'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class_exploded'])


def test_expand_drug_class_only_na():
    expanded_df = RGI_PARSER_ONLY_NA.explode_column('rgi_main.Drug Class')
    assert 2 == len(expanded_df)
    assert ['file1', 'file2'] == expanded_df.index.tolist()

    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class'])

    assert [] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class_exploded'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class_exploded'])


def test_expand_drug_class_only_numpy_nan():
    expanded_df = RGI_PARSER_ONLY_NUMPY_NAN.explode_column('rgi_main.Drug Class')
    assert 2 == len(expanded_df)
    assert ['file1', 'file2'] == expanded_df.index.tolist()

    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class'])

    assert [] == expanded_df['rgi_main.Drug Class_exploded'].dropna().tolist()
    assert pd.isna(expanded_df.loc['file1', 'rgi_main.Drug Class_exploded'])
    assert pd.isna(expanded_df.loc['file2', 'rgi_main.Drug Class_exploded'])


def test_select_by_drugclass_single1():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class1'])

    assert 5 == len(new_parser.df_rgi)
    assert ['file1', 'file1', 'file2', 'file2', 'file2'] == new_parser.df_rgi.index.tolist()
    print(new_parser.df_rgi['rgi_main.Drug Class'].tolist())
    assert ['class1; class2', 'class1; class2; class3',
            'class1; class2; class4', 'class5', ''] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_single2():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class2'])

    assert 5 == len(new_parser.df_rgi)
    assert ['file1', 'file1', 'file2', 'file2', 'file2'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2', 'class1; class2; class3',
            'class1; class2; class4', 'class5', ''] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_single3():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class3'])

    assert 2 == len(new_parser.df_rgi)
    assert ['file1', 'file1'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2', 'class1; class2; class3'] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_single4():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class4'])

    assert 3 == len(new_parser.df_rgi)
    assert ['file2', 'file2', 'file2'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2; class4', 'class5', ''] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_multiple_1_2():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class1', 'class2'])

    assert 5 == len(new_parser.df_rgi)
    assert ['file1', 'file1', 'file2', 'file2', 'file2'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2', 'class1; class2; class3',
            'class1; class2; class4', 'class5', ''] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_multiple_1_3():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class1', 'class3'])

    assert 2 == len(new_parser.df_rgi)
    assert ['file1', 'file1'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2', 'class1; class2; class3'] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_multiple_1_2_3():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class1', 'class2', 'class3'])

    assert 2 == len(new_parser.df_rgi)
    assert ['file1', 'file1'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2', 'class1; class2; class3'] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()


def test_select_by_drugclass_multiple_4_5():
    new_parser = RGI_PARSER.select_by_elements_in_column_split(type='file', column='rgi_main.Drug Class',
                                                               elements=['class4', 'class5'])

    assert 3 == len(new_parser.df_rgi)
    assert ['file2', 'file2', 'file2'] == new_parser.df_rgi.index.tolist()
    assert ['class1; class2; class4', 'class5', ''] == new_parser.df_rgi['rgi_main.Drug Class'].tolist()
