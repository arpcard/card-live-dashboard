from pathlib import Path
from typing import Dict, Any
import yaml
import logging
from datetime import datetime
import shutil
from os import path

logger = logging.getLogger(__name__)


class ConfigManager:

    def __init__(self, card_live_home: Path):
        if card_live_home is None:
            raise Exception('Cannot pass None for card_live_home')

        self._card_live_home = card_live_home
        self._config_file = card_live_home / 'config' / 'cardlive.yaml'

    def read_config(self) -> Dict[Any, Any]:
        """
        Reads the config file and returns a dictionary of the values.
        :return: A dictionary of the values.
        """
        if not self._config_file.exists():
            raise Exception(f'Config file {self._config_file} does not exist')

        with open(self._config_file) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
            if config is None:
                config = {}

            # Some basic syntax checking
            if 'url_base_pathname' not in config:
                config['url_base_pathname'] = '/'
            elif not config['url_base_pathname'].endswith('/'):
                config['url_base_pathname'] = config['url_base_pathname'] + '/'

            return config

    def write_example_config(self):
        """
        Writes an example configuration file to the given directory
        :return: None.
        """
        if self._config_file.exists():
            timepart = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_config = self._config_file / f'.{timepart}.bak'
            logger.warning(f'File [{self._config_file}] exists, backing up to [{backup_config}]')
            shutil.copy(self._config_file, backup_config)

        shutil.copy(Path(path.dirname(__file__)) / 'config' / 'cardlive.yaml', self._config_file)
        logger.info(f'Wrote example configuration to [{self._config_file}]')