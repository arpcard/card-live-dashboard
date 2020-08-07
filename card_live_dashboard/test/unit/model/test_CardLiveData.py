from datetime import datetime
import unittest
from unittest.mock import MagicMock
import pandas as pd
import logging

from card_live_dashboard import RGIParser
from card_live_dashboard.model.CardLiveData import CardLiveData

logger = logging.getLogger('CardLiveDataTest')

TIME_FMT = '%Y-%m-%d %H:%M:%S'


class CardLiveDataTest(unittest.TestCase):

    def setUp(self):
        main_df = pd.DataFrame(
            columns=['filename', 'timestamp'],
            data=[['file1', '2020-08-05 16:27:32.996157'],
                  ['file2', '2020-08-06 16:27:32.996157']
                  ]
        )

        self.other_df = pd.DataFrame(
            columns=['filename', 'timestamp'],
            data=[['file1', '2020-08-05 16:27:32.996157'],
                  ['file2', '2020-08-06 16:27:32.996157']
                  ]
        ).set_index('filename')

        self.rgi_parser = RGIParser(self.other_df)

        self.data = CardLiveData(main_df=main_df,
                                 rgi_parser=self.rgi_parser,
                                 rgi_kmer_df=self.other_df,
                                 lmat_df=self.other_df,
                                 mlst_df=self.other_df)

    def test_select_by_time_keepall(self):
        rgi_parser = self.rgi_parser
        rgi_parser_subset = RGIParser(self.other_df)
        rgi_parser.select_by_files = MagicMock(return_value=rgi_parser_subset)
        rgi_parser_subset.files = MagicMock(return_value=['file1', 'file2'])

        data = self.data
        start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
        end = datetime.strptime('2020-08-07 00:00:00', TIME_FMT)

        self.assertEqual(2, len(self.data), 'Data not initialized to correct number of entries')
        data = data.select_by_time(start, end)
        self.assertEqual(2, len(data), 'Invalid number after selection')
        self.assertEqual(2, len(data.main_df), 'Invalid number after selection')
        self.assertEqual(2, len(data.rgi_kmer_df), 'Invalid number after selection')
        self.assertEqual(2, len(data.mlst_df), 'Invalid number after selection')
        self.assertEqual(2, len(data.lmat_df), 'Invalid number after selection')

    def test_select_by_time_keepone(self):
        rgi_parser = self.rgi_parser
        rgi_parser_subset = RGIParser(self.other_df)
        rgi_parser.select_by_files = MagicMock(return_value=rgi_parser_subset)
        rgi_parser_subset.files = MagicMock(return_value=['file1'])

        data = self.data
        start = datetime.strptime('2020-08-05 00:00:00', TIME_FMT)
        end = datetime.strptime('2020-08-06 00:00:00', TIME_FMT)

        self.assertEqual(2, len(self.data), 'Data not initialized to correct number of entries')
        data = data.select_by_time(start, end)
        self.assertEqual(1, len(data), 'Invalid number after selection')
        self.assertEqual(1, len(data.main_df), 'Invalid number after selection')
        self.assertEqual(1, len(data.rgi_kmer_df), 'Invalid number after selection')
        self.assertEqual(1, len(data.mlst_df), 'Invalid number after selection')
        self.assertEqual(1, len(data.lmat_df), 'Invalid number after selection')
