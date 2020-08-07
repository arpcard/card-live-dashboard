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

RGI_PARSER = RGIParser(OTHER_DF)

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
    assert 2 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
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
    assert 1 == len(data.rgi_parser.df_rgi), 'Invalid number after selection'
    assert 1 == len(data.rgi_kmer_df), 'Invalid number after selection'
    assert 1 == len(data.lmat_df), 'Invalid number after selection'
    assert 1 == len(data.mlst_df), 'Invalid number after selection'
