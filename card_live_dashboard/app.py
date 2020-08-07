import dash
from pathlib import Path
from os import path

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData
import card_live_dashboard.layouts as layouts
import card_live_dashboard.callbacks as callbacks

DEFAULT_DATA_DIR = Path(path.dirname(__file__), '..', 'data', 'card_live')


def build_app(card_live_data_dir: Path = DEFAULT_DATA_DIR) -> dash.dash.Dash:
    """
    Builds the CARD:Live Dash application.
    :param card_live_data_dir: The directory containing the CARD:Live data.
    :return:
    """
    app = dash.Dash(__name__, external_stylesheets=layouts.external_stylesheets)

    data_loader = CardLiveDataLoader(card_live_data_dir)
    CardLiveData.create_instance(data_loader)

    app.layout = layouts.default_layout()
    callbacks.build_callbacks(app)

    return app
