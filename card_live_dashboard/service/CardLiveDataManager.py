from __future__ import annotations
from pathlib import Path

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData


class CardLiveDataManager:
    INSTANCE = None

    def __init__(self, card_live_dir: Path):
        self._data_loader = CardLiveDataLoader(card_live_dir)
        self._card_live_data = self._data_loader.update_data()

    @property
    def card_data(self) -> CardLiveData:
        return self._card_live_data

    @classmethod
    def create_instance(cls, card_live_dir: Path) -> None:
        cls.INSTANCE = CardLiveDataManager(card_live_dir)

    @classmethod
    def get_instance(cls) -> CardLiveDataManager:
        if cls.INSTANCE is not None:
            return cls.INSTANCE
        else:
            raise Exception(f'{cls} does not yet have an instance.')
