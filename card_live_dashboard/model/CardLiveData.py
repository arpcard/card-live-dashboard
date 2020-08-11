from __future__ import annotations
from typing import Set, List, Union
from datetime import datetime
import pandas as pd

from card_live_dashboard.model.RGIParser import RGIParser


class CardLiveData:
    INSTANCE = None

    def __init__(self, main_df: pd.DataFrame, rgi_parser: RGIParser, rgi_kmer_df: pd.DataFrame,
                 lmat_df: pd.DataFrame, mlst_df: pd.DataFrame):
        self._main_df = main_df.reset_index().set_index('filename').astype({'geo_area_code': 'int64'})
        self._main_df['timestamp'] = pd.to_datetime(self._main_df['timestamp'])
        self._rgi_parser = rgi_parser
        self._rgi_kmer_df = rgi_kmer_df
        self._lmat_df = lmat_df
        self._mlst_df = mlst_df

    def select(self, table: str, by: str, **kwargs) -> CardLiveData:
        """
        Selects data from the CardLiveData object based on the matched criteria.
        :param table: The particular table of data to select from ['main', 'rgi'].
        :param by: The type of selection to perform. See underlying implementation classes
                      for the particular table (either this class or RGIParser) for details.
        :param kwargs: Additional arguments for the underlying selection method.
        :return: A new CardLiveData object which matches the passed criteria.
        """
        if table == 'main':
            if by == 'time':
                return self.select_by_time(**kwargs)
            elif by == 'lmat_taxonomy':
                return self.select_by_taxonomy(column='lmat_taxonomy', **kwargs)
            elif by == 'rgi_kmer_taxonomy':
                return self.select_by_taxonomy(column='rgi_kmer_taxonomy', **kwargs)
            else:
                raise Exception(f'Unknown value[by={by}]')
        elif table == 'rgi':
            rgi_parser_subset = self.rgi_parser.select(by=by, **kwargs)
            return self.select_from_rgi_parser(rgi_parser_subset)
        else:
            raise Exception(f'Unknown value [table={table}].')

    def select_by_time(self, start: datetime, end: datetime) -> CardLiveData:
        """
        Selects the data within the start and end time periods.
        :param start: The start time.
        :param end: The end time.

        :return: A CardLiveData object on the subset of matched data.
        """
        files = set(self.main_df[
                        (self.main_df['timestamp'] >= start) & (self.main_df['timestamp'] <= end)].index.tolist())
        return self.select_by_files(files)

    def select_by_taxonomy(self, column: str, taxonomy: Union[List, str]) -> CardLiveData:
        if taxonomy is None or taxonomy == [] or taxonomy == '':
            return self
        else:
            files = set(self.main_df[self.main_df[column] == taxonomy].index.tolist())
            return self.select_by_files(files)

    def select_from_rgi_parser(self, rgi_parser: RGIParser):
        """
        Selects a subset of data based on the results in the passed RGIParser.
        :param rgi_parser: The RGIParser to select from.
        :return: The subset of data from data in the passed RGIParser.
        """
        files = rgi_parser.files()
        main_df_subset = self.main_df.loc[files]
        rgi_kmer_subset = self.rgi_kmer_df.loc[files]
        lmat_subset = self.lmat_df.loc[files]
        mlst_subset = self.mlst_df.loc[files]

        return CardLiveData(
            main_df=main_df_subset,
            rgi_parser=rgi_parser,
            rgi_kmer_df=rgi_kmer_subset,
            lmat_df=lmat_subset,
            mlst_df=mlst_subset
        )

    def select_by_files(self, files: Set[str]) -> CardLiveData:
        """
        Selects a subset of data based on the set of files.
        :param files: The set of files to select by.
        :return: Those results on the subset of the passed files.
        """
        rgi_parser_subset = self.rgi_parser.select_by_files(files)
        return self.select_from_rgi_parser(rgi_parser_subset)

    def files(self) -> Set[str]:
        """
        Returns the set of files in this object.

        :return: The set of files in this object.
        """
        return set(self.main_df.index.tolist())

    def unique_column(self, col: str) -> Set[str]:
        """
        Returns the set of unique values in a column.

        :param col: The column to select.
        :return: The set of unique values in a column.
        """
        return set(self.main_df[col].tolist())

    def samples_count(self) -> int:
        return len(self._main_df)

    def latest_update(self) -> datetime:
        return self.main_df['timestamp'].max()

    def value_counts(self, cols: List[str], include_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Given a list of columns, counts the number of files in the underlying dataframe for each category of that column.

        :param cols: The columns to count by.
        :param include_df: An additional table to merge onto the main table to count by additional information.
        :return: A dataframe with counts by the given column's values.
        """
        if include_df is not None:
            reduced_frame = self.main_df.merge(include_df, how='left', left_index=True, right_index=True)
        else:
            reduced_frame = self.main_df

        reduced_frame = reduced_frame.groupby('filename').first()
        counts_frame = reduced_frame[cols].groupby(cols).size().to_frame()
        return counts_frame.rename(columns={0: 'count'})

    def __len__(self) -> int:
        return self.samples_count()

    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def main_df(self) -> pd.DataFrame:
        return self._main_df

    @property
    def rgi_parser(self) -> RGIParser:
        return self._rgi_parser

    @property
    def rgi_df(self) -> pd.DataFrame:
        return self._rgi_parser.df_rgi

    @property
    def rgi_kmer_df(self) -> pd.DataFrame:
        return self._rgi_kmer_df

    @property
    def lmat_df(self) -> pd.DataFrame:
        return self._lmat_df

    @property
    def mlst_df(self) -> pd.DataFrame:
        return self._mlst_df
