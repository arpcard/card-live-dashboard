from __future__ import annotations
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData

logger = logging.getLogger(__name__)


class CardLiveDataManager:
    INSTANCE = None

    def __init__(self, card_live_dir: Path):
        self._data_loader = CardLiveDataLoader(card_live_dir)
        self._card_live_data = self._data_loader.read_or_update_data()

        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(self.update_job, 'interval', seconds=15)
        self._scheduler.start()

    def update_job(self):
        logger.debug('Updating CARD:Live data.')
        card_live_data = self._data_loader.read_or_update_data(self._card_live_data)
        logger.debug(f'Old data has {len(self._card_live_data)} samples, new data has {len(card_live_data)} samples')
        self._card_live_data = card_live_data
        logger.debug('Finished updating CARD:Live data.')

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
