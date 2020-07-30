import pandas as pd

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader


class CardLiveData:
    INSTANCE = None

    def __init__(self, data_loader: CardLiveDataLoader):
        self._main_df = data_loader.main_df
        self._rgi_df = data_loader.rgi_df
        self._rgi_kmer_df = data_loader.rgi_kmer_df
        self._lmat_df = data_loader.lmat_df
        self._mlst_df = data_loader.mlst_df

    @property
    def main_df(self) -> pd.DataFrame:
        return self._main_df

    @property
    def rgi_df(self) -> pd.DataFrame:
        return self._rgi_df

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
    def create_instance(cls, data_loader: CardLiveDataLoader):
        cls.INSTANCE = CardLiveData(data_loader)

    @classmethod
    def get_data_package(cls):
        if cls.INSTANCE != None:
            return cls.INSTANCE
        else:
            raise Exception(f'{cls} does not yet have an instance.')