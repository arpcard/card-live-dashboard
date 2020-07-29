import dash
import card_live_dashboard.layouts as layouts

app = dash.Dash(__name__, external_stylesheets=layouts.external_stylesheets)