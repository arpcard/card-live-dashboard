import dash
from pathlib import Path
from os import path

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData
import card_live_dashboard.layouts as layouts
from card_live_dashboard.callbacks import build_callbacks

app = dash.Dash(__name__, external_stylesheets=layouts.external_stylesheets)

data_loader = CardLiveDataLoader(Path(path.dirname(__file__), '..', 'data', 'card_live'))
CardLiveData.create_instance(data_loader)

app.layout = layouts.default_layout()
build_callbacks(app)
