from pathlib import Path
from os import path

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser
import card_live_dashboard.layouts as layouts
import card_live_dashboard.callbacks as callbacks
from card_live_dashboard.app import app

data_loader = CardLiveDataLoader(Path(path.dirname(__file__), '..', 'data', 'card_live'))
CardLiveData.create_instance(data_loader)

app.layout = layouts.default_layout()