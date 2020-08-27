from typing import Union
import dash
import flask
from pathlib import Path
from os import getcwd

from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
import card_live_dashboard.layouts as layouts
import card_live_dashboard.callbacks as callbacks

DEFAULT_CARD_LIVE_HOME = getcwd()


def build_app(card_live_home: Path = DEFAULT_CARD_LIVE_HOME) -> dash.dash.Dash:
    """
    Builds the CARD:Live Dash application.
    :param card_live_home: The home directory of CARD:Live.
    :return: The Dash application.
    """
    if not card_live_home.exists():
        raise Exception(f'Error: card live home [{card_live_home}] does not exist. Please specify the appropriate directory.')

    card_live_data_dir = Path(card_live_home, 'data', 'card_live')
    if not card_live_data_dir.exists():
        raise Exception((f'Error: card live data directory [{card_live_data_dir}] does not exist. '
                         'Please check for this directory or change card_live_home to something '
                         f'other than [{card_live_home}]'))

    app = dash.Dash(name=__name__, external_stylesheets=layouts.external_stylesheets)

    CardLiveDataManager.create_instance(card_live_home)

    app.layout = layouts.default_layout()
    callbacks.build_callbacks(app)

    return app


def flask_app(card_live_home: Union[str,Path] = DEFAULT_CARD_LIVE_HOME) -> flask.Flask:
    """
    Builds and gets the Flask app object for deployment as a Flask app.
    :param card_live_home: The home directory for CARD:Live.
    :return: The Flask app server object.
    """
    if isinstance(card_live_home, str):
        data_dir = Path(card_live_home)

    return build_app(card_live_home).server