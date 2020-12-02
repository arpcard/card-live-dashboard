from __future__ import annotations

import logging
from pathlib import Path
from typing import Generator, List, Set, Union

import numpy as np
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.data_modifiers.AddGeographicNamesModifier import AddGeographicNamesModifier
from card_live_dashboard.model.data_modifiers.AddTaxonomyModifier import AddTaxonomyModifier
from card_live_dashboard.model.data_modifiers.AntarcticaNAModifier import AntarcticaNAModifier
from card_live_dashboard.service import region_codes
from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader

logger = logging.getLogger(__name__)


class CardLiveDataManager:
    INSTANCE = None

    def __init__(self, cardlive_home: Path):
        ncbi_db_path = cardlive_home / 'db' / 'taxa.sqlite'
        card_live_data_dir = cardlive_home / 'data' / 'card_live'

        self._data_loader = CardLiveDataLoader(card_live_data_dir)
        self._data_loader.add_data_modifiers([
            AntarcticaNAModifier(np.datetime64('2020-07-20')),
            AddGeographicNamesModifier(region_codes),
            AddTaxonomyModifier(ncbi_db_path),
        ])

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

    def data_archive_generator(self, file_names: Union[List[str], Set[str]] = None) -> Generator[bytes, None, None]:
        """
        Get the CARD:Live JSON files as a zipstream generator.
        :param file_names: The file names to load into the archive.
        :return: A generator which allows streaming of the zip file contents.
        """
        if file_names is None:
            file_names = self.card_data.files()

        return self._data_loader.data_archive_generator(file_names)

    @property
    def card_data(self) -> CardLiveData:
        return self._card_live_data

    @classmethod
    def create_instance(cls, cardlive_home: Path) -> None:
        cls.INSTANCE = CardLiveDataManager(cardlive_home)

    @classmethod
    def get_instance(cls) -> CardLiveDataManager:
        if cls.INSTANCE is not None:
            return cls.INSTANCE
        else:
            raise Exception(f'{cls} does not yet have an instance.')
