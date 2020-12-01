from os import getcwd
from pathlib import Path
from typing import Union

import dash
import flask

import card_live_dashboard.callbacks as callbacks
import card_live_dashboard.layouts as layouts
import card_live_dashboard.routes as routes
from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
from card_live_dashboard.service.ConfigManager import ConfigManager

DEFAULT_CARD_LIVE_HOME = Path(getcwd())


def build_app(card_live_home: Path = DEFAULT_CARD_LIVE_HOME) -> dash.dash.Dash:
    """
    Builds the CARD:Live Dash application.
    :param card_live_home: The home directory of CARD:Live.
    :return: The Dash application.
    """
    if not card_live_home.exists():
        raise Exception(
            f'Error: card live home [{card_live_home}] does not exist. Please specify the appropriate directory.')

    card_live_data_dir = Path(card_live_home, 'data', 'card_live')
    if not card_live_data_dir.exists():
        raise Exception((f'Error: card live data directory [{card_live_data_dir}] does not exist. '
                         'Please check for this directory or change card_live_home to something '
                         f'other than [{card_live_home}]'))

    config_manager = ConfigManager(card_live_home)
    config = config_manager.read_config()

    app = dash.Dash(name=__name__,
                    external_stylesheets=layouts.external_stylesheets,
                    url_base_pathname=config['url_base_pathname'])

    CardLiveDataManager.create_instance(card_live_home)

    app.layout = layouts.default_layout(config['url_base_pathname'])
    app.title = 'CARD:Live Dashboard'
    callbacks.build_callbacks(app)

    routes.create_flask_routes(app.server, config['url_base_pathname'], card_live_data_dir)

    return app


def flask_app(card_live_home: Union[str, Path] = DEFAULT_CARD_LIVE_HOME) -> flask.Flask:
    """
    Builds and gets the Flask app object for deployment as a Flask app.
    :param card_live_home: The home directory for CARD:Live.
    :return: The Flask app server object.
    """
    if isinstance(card_live_home, str):
        card_live_home = Path(card_live_home)

    return build_app(card_live_home).server


def read_config(card_live_home: Path):
    """
    Reads the config file
    :param card_live_home:
    :return:
    """
