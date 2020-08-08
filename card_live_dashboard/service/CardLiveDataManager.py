from __future__ import annotations
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
import logging

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData

logger = logging.getLogger(__name__)


class CardLiveDataManager:
    INSTANCE = None

    def __init__(self, card_live_dir: Path):
        self._data_loader = CardLiveDataLoader(card_live_dir)
        self._card_live_data = self._data_loader.read_or_update_data()

        self._scheduler = BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            executors={
                'default': ThreadPoolExecutor(1)
            },
            job_defaults={
                'max_instances': 1
            }
        )
        self._scheduler.add_job(self.update_job, 'interval', minutes=10)
        self._scheduler.start()

    def update_job(self):
        logger.debug('Updating CARD:Live data.')
        try:
            new_data = self._data_loader.read_or_update_data(self._card_live_data)
            if new_data is not self._card_live_data:
                logger.debug(f'Old data has {len(self._card_live_data)} samples, new data has {len(new_data)} samples')
                self._card_live_data = new_data
        except Exception as e:
            logger.info('An exeption occured when attempting to load new data. Skipping new data.')
            logger.exception(e)
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
