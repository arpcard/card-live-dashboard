from __future__ import annotations
from datetime import datetime
import pandas as pd

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.RGIParser import RGIParser


class CardLiveData:
    INSTANCE = None

    def __init__(self, main_df: pd.DataFrame, rgi_parser: RGIParser, rgi_kmer_df: pd.DataFrame,
                 lmat_df: pd.DataFrame, mlst_df: pd.DataFrame):
        self._main_df = main_df
        self._rgi_parser = rgi_parser
        self._rgi_kmer_df = rgi_kmer_df
        self._lmat_df = lmat_df
        self._mlst_df = mlst_df

    def select(self, table: str, **kwargs) -> CardLiveData:
        """
        Selects data from the CardLiveData object based on the matched criteria.
        :param table: The particular table of data to select from ['main', 'rgi'].
        :param kwargs: Additional arguments for the underlying selection method.
        :return: A new CardLiveData object which matches the passed criteria.
        """
        if table == 'rgi':
            rgi_parser_subset = self.rgi_parser.select(**kwargs)
            files = rgi_parser_subset.files()
            main_df_subset = self.main_df.loc[files]
            rgi_kmer_subset = self.rgi_kmer_df.loc[files]
            lmat_subset = self.lmat_df.loc[files]
            mlst_subset = self.mlst_df.loc[files]

            return CardLiveData(
                main_df=main_df_subset,
                rgi_parser=rgi_parser_subset,
                rgi_kmer_df=rgi_kmer_subset,
                lmat_df=lmat_subset,
                mlst_df=mlst_subset
            )
        else:
            raise Exception(f'Unknown value [table={table}].')

    def samples_count(self) -> int:
        return len(self._main_df)

    def latest_update(self) -> datetime:
        return self.main_df['timestamp'].max()

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

    @classmethod
    def from_data_loader(cls, data_loader: CardLiveDataLoader) -> CardLiveData:
        return CardLiveData(
            main_df=data_loader.main_df,
            rgi_parser=RGIParser(data_loader.rgi_df),
            rgi_kmer_df=data_loader.rgi_kmer_df,
            lmat_df=data_loader.lmat_df,
            mlst_df=data_loader.mlst_df,
        )

    @classmethod
    def create_instance(cls, data_loader: CardLiveDataLoader) -> None:
        cls.INSTANCE = cls.from_data_loader(data_loader)

    @classmethod
    def get_data_package(cls) -> CardLiveData:
        if cls.INSTANCE is not None:
            return cls.INSTANCE
        else:
            raise Exception(f'{cls} does not yet have an instance.')