from typing import Union
import dash
import flask
from pathlib import Path
from os import path

from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
import card_live_dashboard.layouts as layouts
import card_live_dashboard.callbacks as callbacks

DEFAULT_DATA_DIR = Path(path.dirname(__file__), '..', 'data', 'card_live')


def build_app(card_live_data_dir: Path = DEFAULT_DATA_DIR) -> dash.dash.Dash:
    """
    Builds the CARD:Live Dash application.
    :param card_live_data_dir: The directory containing the CARD:Live data.
    :return: The Dash application.
    """
    app = dash.Dash(name=__name__, external_stylesheets=layouts.external_stylesheets)

    CardLiveDataManager.create_instance(card_live_data_dir)

    app.layout = layouts.default_layout()
    callbacks.build_callbacks(app)

    return app


def flask_app(data_dir: Union[str,Path] = DEFAULT_DATA_DIR) -> flask.Flask:
    """
    Builds and gets the Flask app object for deployment as a Flask app.
    :param data_dir: The directory containing the data.
    :return: The Flask app server object.
    """
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    return build_app(data_dir).server