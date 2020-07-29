from pathlib import Path
from os import path

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.RGIParser import RGIParser
import card_live_dashboard.layouts as layouts
import card_live_dashboard.callbacks as callbacks
from card_live_dashboard.app import app

data = CardLiveDataLoader(Path(path.dirname(__file__), '..', 'data', 'card_live_small'))
rgi_parser = RGIParser(data.rgi_df)
callbacks.rgi_parser = rgi_parser
callbacks.data = data

all_drugs = rgi_parser.all_drugs_list()

number_of_samples = len(data.main_df)
last_updated = data.main_df['timestamp'].max()

app.layout = layouts.default_layout(number_of_samples, last_updated, all_drugs)