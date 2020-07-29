from typing import List
from datetime import datetime, timedelta
from dash.dependencies import Input, Output

from card_live_dashboard.model.RGIParser import RGIParser
import card_live_dashboard.layouts.figures as figures

rgi_parser: RGIParser = None
region_codes = None
data = None
world = None

