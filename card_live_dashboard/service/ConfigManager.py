from pathlib import Path
import yaml


class ConfigManager:

    def __init__(self, card_live_home: Path):
        if card_live_home is None:
            raise Exception('Cannot pass None for card_live_home')

        self._card_live_home = card_live_home
        self._config_file = card_live_home / 'config' / 'cardlive.yaml'

        if not self._config_file.exists():
            raise Exception(f'Config file {self._config_file} does not exist')

    def read_config(self):
        """
        Reads the config file and returns a dictionary of the values.
        :return: A dictionary of the values.
        """
        with open(self._config_file) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

            # Some basic syntax checking
            if 'url_base_pathname' not in config:
                config['url_base_pathname'] = '/'
            elif not config['url_base_pathname'].endswith('/'):
                config['url_base_pathname'] = config['url_base_pathname'] + '/'

            return config
