from datetime import datetime
import pandas as pd

from card_live_dashboard import RGIParser
from card_live_dashboard.model.CardLiveData import CardLiveData

TIME_FMT = '%Y-%m-%d %H:%M:%S'

MAIN_DF = pd.DataFrame(
    columns=['filename', 'timestamp'],
    data=[['file1', '2020-08-05 16:27:32.996157'],
          ['file2', '2020-08-06 16:27:32.996157']
          ]
)

OTHER_DF = pd.DataFrame(
    columns=['filename', 'timestamp'],
    data=[['file1', '2020-08-05 16:27:32.996157'],
          ['file2', '2020-08-06 16:27:32.996157']
          ]
).set_index('filename')

RGI_DF = pd.DataFrame(
    columns=['filename', 'timestamp', 'rgi_main.Cut_Off', 'rgi_main.Drug Class'],
    data=[['file1', '2020-08-05 16:27:32.996157', 'Perfect', 'class1; class2'],
          ['file1', '2020-08-05 16:27:32.996157', 'Strict', 'class1; class2; class3'],
          ['file2', '2020-08-06 16:27:32.996157', 'Perfect', 'class1; class4']
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
    end = datetime.strptime('2020-08-07 00:00:00', TIME_FMT)

    assert 2 == len(data), 'Data not initialized to correct number of entries'
    data = data.select_by_time(start, end)
    assert 2 == len(data), 'Invalid number after selection'
    assert 2 == len(data.main_df), 'Invalid number after selection'
    assert {'file1', 'file2'} == data.files(), 'Invalid files'
    assert 3 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 2 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 2 == len(data.lmat_df), 'Invalid number after selection'
    assert 2 == len(data.mlst_df), 'Invalid number after selection'


def test_select_by_time_keepone():
    data = DATA
    start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
    end = datetime.strptime('2020-08-06 00:00:00', TIME_FMT)

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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

    assert 2 == len(data), 'Data not initialized to correct number of entries'
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
