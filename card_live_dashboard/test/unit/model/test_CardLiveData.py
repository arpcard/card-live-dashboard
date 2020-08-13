from datetime import datetime
import pandas as pd
import numpy as np

from card_live_dashboard.model.RGIParser import RGIParser
from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.data_modifiers.AntarcticaNAModifier import AntarcticaNAModifier

TIME_FMT = '%Y-%m-%d %H:%M:%S'

MAIN_DF = pd.DataFrame(
    columns=['filename', 'timestamp', 'geo_area_code', 'lmat_taxonomy', 'rgi_kmer_taxonomy'],
    data=[['file1', '2020-08-05 16:27:32.996157', 10, 'Salmonella enterica', 'Enterobacteriaceae'],
          ['file2', '2020-08-06 16:27:32.996157', 10, 'Enterobacteriaceae', 'Salmonella enterica'],
          ['file3', '2020-08-07 16:27:32.996157', 1, 'Salmonella enterica', 'Enterobacteriaceae'],
          ],
)

OTHER_DF = pd.DataFrame(
    columns=['filename'],
    data=[['file1'],
          ['file2'],
          ['file3'],
          ]
).set_index('filename')

RGI_DF = pd.DataFrame(
    columns=['filename', 'rgi_main.Cut_Off', 'rgi_main.Drug Class', 'rgi_main.Best_Hit_ARO'],
    data=[['file1', 'Perfect', 'class1; class2', 'gene1'],
          ['file1', 'Strict', 'class1; class2; class3', 'gene2'],
          ['file2', 'Perfect', 'class1; class2; class4', 'gene1'],
          ['file3', None, None, None],
          ]
).set_index('filename')

RGI_PARSER = RGIParser(RGI_DF)

DATA = CardLiveData(main_df=MAIN_DF,
                    rgi_parser=RGI_PARSER,
                    rgi_kmer_df=OTHER_DF,
                    lmat_df=OTHER_DF,
                    mlst_df=OTHER_DF)


def test_select_by_time_keepall():
    data = DATA
    start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
    end = datetime.strptime('2020-08-08 00:00:00', TIME_FMT)

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select_by_time(start, end)
    assert 3 == len(data), 'Invalid number after selection'
    assert 3 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2', 'file3'} == data.files(), 'Invalid files'
    assert 4 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 3 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 3 == len(data.lmat_df), 'Invalid number after selection'
    assert 3 == len(data.mlst_df), 'Invalid number after selection'


def test_select_by_time_keepone():
    data = DATA
    start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
    end = datetime.strptime('2020-08-06 00:00:00', TIME_FMT)

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select_by_time(start, end)
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file1'} == data.files(), 'Invalid files'
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_by_time_keepnone():
    data = DATA
    start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
    end = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select_by_time(start, end)
    assert 0 == len(data), 'Invalid number after selection'
    assert 0 == len(data.main_df), 'Invalid number after selection'
    assert 0 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 0 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 0 == len(data.lmat_df), 'Invalid number after selection'
    assert 0 == len(data.mlst_df), 'Invalid number after selection'


def test_select_time_keepone():
    data = DATA
    start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
    end = datetime.strptime('2020-08-06 00:00:00', TIME_FMT)

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='main', by='time', start=start, end=end)
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file1'} == data.files(), 'Invalid files'
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_parser_keepone():
    data = DATA
    rgi_parser = RGIParser(RGI_DF.loc['file1'])

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select_from_rgi_parser(rgi_parser)
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file1'} == data.files(), 'Invalid files'
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_cutoff_perfect():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='cutoff', type='row', level='perfect')
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2'} == data.files(), 'Invalid files'
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'Perfect'} == set(data.rgi_parser.df_rgi['rgi_main.Cut_Off'].tolist()), 'Invalid cutoff values'
    assert {'class1', 'class2', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_cutoff_strict():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='cutoff', type='row', level='strict')
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file1'} == data.files(), 'Invalid files'
    assert 1 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'Strict'} == set(data.rgi_parser.df_rgi['rgi_main.Cut_Off'].tolist()), 'Invalid cutoff values'
    assert {'class1', 'class2', 'class3'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_cutoff_all():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='cutoff', type='row', level='all')
    assert 3 == len(data), 'Invalid number after selection'
    assert 3 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2', 'file3'} == data.files(), 'Invalid files'
    assert 4 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'Strict', 'Perfect', None} == set(
        data.rgi_parser.df_rgi['rgi_main.Cut_Off'].tolist()), 'Invalid cutoff values'
    assert {'class1', 'class2', 'class3', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 3 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 3 == len(data.lmat_df), 'Invalid number after selection'
    assert 3 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_drugclass_all():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='drug', type='file', drug_classes=[])
    assert 3 == len(data), 'Invalid number after selection'
    assert 3 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2', 'file3'} == data.files(), 'Invalid files'
    assert 4 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'class1', 'class2', 'class3', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 3 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 3 == len(data.lmat_df), 'Invalid number after selection'
    assert 3 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_drugclass_one():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='drug', type='file', drug_classes=['class1'])
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'class1', 'class2', 'class3', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_drugclass_two():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='drug', type='file', drug_classes=['class1', 'class2'])
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'class1', 'class2', 'class3', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_drugclass_three():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='drug', type='file', drug_classes=['class1', 'class2', 'class4'])
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file2'} == data.files(), 'Invalid files'
    assert 1 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'class1', 'class2', 'class4'} == data.rgi_parser.all_drugs(), 'Invalid drug classes'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_amr_genes_all():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='amr_gene', type='file', amr_genes=[])
    assert 3 == len(data), 'Invalid number after selection'
    assert 3 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2', 'file3'} == data.files(), 'Invalid files'
    assert 4 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes categories'
    assert 3 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 3 == len(data.lmat_df), 'Invalid number after selection'
    assert 3 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_amr_genes_one():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='amr_gene', type='file', amr_genes=['gene1'])
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes categories'
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_rgi_amr_gene_two():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='rgi', by='amr_gene', type='file', amr_genes=['gene1', 'gene2'])
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file1'} == data.files(), 'Invalid files'
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes categories'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_value_counts_geo():
    data = DATA

    counts = data.value_counts(['geo_area_code'])
    assert len(counts) == 2, 'Invalid number of geographic areas'
    assert {'count'} == set(counts.columns.tolist()), 'Invalid columns'
    assert counts.loc[10, 'count'] == 2, 'Invalid count number'
    assert counts.loc[1, 'count'] == 1, 'Invalid count number'


def test_value_counts_timestamp():
    data = DATA

    counts = data.value_counts(['timestamp'])
    assert len(counts) == 3, 'Invalid number of timestamps areas'


def test_value_counts_new_data():
    data = DATA

    new_data = pd.DataFrame(
        columns=['filename', 'color'],
        data=[['file1', 'red'],
              ['file2', 'blue'],
              ['file3', 'red'],
              ]
        ).set_index('filename')

    counts = data.value_counts(cols=['color'], include_df=new_data)
    assert len(counts) == 2, 'Invalid number of unique categories'
    assert {'count'} == set(counts.columns.tolist()), 'Invalid columns'
    assert counts.loc['red', 'count'] == 2, 'Invalid count number'
    assert counts.loc['blue', 'count'] == 1, 'Invalid count number'


def test_value_counts_new_data_multiple_files():
    data = DATA

    new_data = pd.DataFrame(
        columns=['filename', 'color'],
        data=[['file1', 'red'],
              ['file1', 'red'],
              ['file2', 'blue'],
              ['file3', 'red'],
              ]
        ).set_index('filename')

    counts = data.value_counts(cols=['color'], include_df=new_data)
    assert len(counts) == 2, 'Invalid number of unique categories'
    assert {'count'} == set(counts.columns.tolist()), 'Invalid columns'
    assert counts.loc['red', 'count'] == 2, 'Invalid count number'
    assert counts.loc['blue', 'count'] == 1, 'Invalid count number'


def test_select_organism_lmat_all():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='main', by='lmat_taxonomy', taxonomy=None)
    assert 3 == len(data), 'Invalid number after selection'
    assert 3 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2', 'file3'} == data.files(), 'Invalid files'
    assert 4 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes'
    assert ['Salmonella enterica', 'Enterobacteriaceae', 'Salmonella enterica'] == data.main_df['lmat_taxonomy'].tolist()
    assert 3 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 3 == len(data.lmat_df), 'Invalid number after selection'
    assert 3 == len(data.mlst_df), 'Invalid number after selection'


def test_select_organism_rgi_kmer_one():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='main', by='rgi_kmer_taxonomy', taxonomy='Salmonella enterica')
    assert 1 == len(data), 'Invalid number after selection'
    assert 1 == len(data.main_df), 'Invalid number after selection'
    assert {'file2'} == data.files(), 'Invalid files'
    assert 1 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes'
    assert ['Salmonella enterica'] == data.main_df['rgi_kmer_taxonomy'].tolist()
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'


def test_select_organism_lmat_two():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='main', by='lmat_taxonomy', taxonomy='Salmonella enterica')
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file3'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes'
    assert ['Salmonella enterica', 'Salmonella enterica'] == data.main_df['lmat_taxonomy'].tolist()
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_organism_rgi_kmer_two():
    data = DATA

    assert 3 == len(data), 'Data not initialized to correct number of entries'
    data = data.select(table='main', by='rgi_kmer_taxonomy', taxonomy='Enterobacteriaceae')
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file3'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert {'gene1', 'gene2'} == data.rgi_parser.all_amr_genes(), 'Invalid AMR genes'
    assert ['Enterobacteriaceae', 'Enterobacteriaceae'] == data.main_df['rgi_kmer_taxonomy'].tolist()
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_unique_column():
    assert {'Salmonella enterica', 'Enterobacteriaceae'} == DATA.unique_column('lmat_taxonomy')
    assert {'Salmonella enterica', 'Enterobacteriaceae'} == DATA.unique_column('rgi_kmer_taxonomy')
    assert {1, 10} == DATA.unique_column('geo_area_code')


def test_switch_antarctica_na():
    antarctica_modifier = AntarcticaNAModifier(np.datetime64('2020-08-06'))
    data = antarctica_modifier.modify(DATA)

    assert -10 == data.main_df.loc['file1', 'geo_area_code']
    assert 10 == data.main_df.loc['file2', 'geo_area_code']
    assert 1 == data.main_df.loc['file3', 'geo_area_code']


def test_switch_antarctica_na_all():
    antarctica_modifier = AntarcticaNAModifier(np.datetime64('2020-09-01'))
    data = antarctica_modifier.modify(DATA)

    assert -10 == data.main_df.loc['file1', 'geo_area_code']
    assert -10 == data.main_df.loc['file2', 'geo_area_code']
    assert 1 == data.main_df.loc['file3', 'geo_area_code']


def test_switch_antarctica_na_none():
    antarctica_modifier = AntarcticaNAModifier(np.datetime64('2020-07-01'))
    data = antarctica_modifier.modify(DATA)

    assert 10 == data.main_df.loc['file1', 'geo_area_code']
    assert 10 == data.main_df.loc['file2', 'geo_area_code']
    assert 1 == data.main_df.loc['file3', 'geo_area_code']
