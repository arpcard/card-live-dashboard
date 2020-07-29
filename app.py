from typing import List

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.GeographicRegionCodes import GeographicRegionCodes
from card_live_dashboard.model.GeographicSummaries import GeographicSummaries
from card_live_dashboard.model.TaxonomicParser import TaxonomicParser
from card_live_dashboard.model.RGIParser import RGIParser
import card_live_dashboard.layouts.figures as figures
    
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_dir = 'data'
data = CardLiveDataLoader(Path(data_dir, 'card_live_small'))
region_codes = GeographicRegionCodes(Path('card_live_dashboard', 'model', 'data', 'UN-M49', 'UNSD-Methodology.csv'))
summaries = GeographicSummaries(region_codes)
world = region_codes.get_un_m49_regions_naturalearth()

rgi_parser = RGIParser(data.rgi_df)
all_drugs = rgi_parser.all_drugs_list()

side_panel_section_style = {
    'padding': '10px'
}

number_of_samples = len(data.main_df)
last_updated = data.main_df['timestamp'].max()

app.layout = html.Div(className='container-fluid', children=[
    html.Div(className='row', children=[
        html.Div(className='col-sm-3', children=[
            html.Div(className='sticky-top', children=[
                html.H1([
                    'CARD:Live'
                ]),
                html.Span(className='badge badge-secondary', children=[f'{number_of_samples} samples']),
                ' ',
                html.Span(className='badge badge-secondary', children=[f'Last updated: {last_updated: %b %d, %Y}']),
                html.Div(children=['Filter display by drug class: ',
                        dcc.Dropdown(
                            id='drug-class-select',
                            options=[{'label': x, 'value': x} for x in all_drugs],
                            multi=True,
                            placeholder='Select a drug class',
                            style={'color': 'black'},
                        ),
                    ], style=side_panel_section_style),
                html.Div(children=['Select a time period: ',
                                  dcc.Dropdown(id='time-period-items',
                                               value='all',
                                               clearable=False,
                                              style={'color': 'black'})
                ], style=side_panel_section_style),
                html.P(className='text-center', children=[
                    html.Br(),
                    html.A(className='badge badge-primary', children=['Code | GitLab'], href='https://devcard.mcmaster.ca:8888/apetkau/amr-visualization-summer-2020'),
                ]),
            ]),
        ], style={'background-color': '#2c3e50', 'color': 'white'}),
        html.Div(className='col', children = [
            dcc.Loading(children=[
                html.Div(className='container', children=[
                    html.Div(className='row', children=[html.Div(className='col', id='main-pane')]),
                ])
            ]),
        ], style={'background-color': 'white'})
    ]),
], style={'background-color': '##2c3e50'})

@app.callback(
    [Output('main-pane', 'children'),
     Output('time-period-items', 'options')],
    [Input('drug-class-select', 'value'),
     Input('time-period-items', 'value')]
)
def update_geo_time_figure(drug_classes: List[str], time_dropdown):
    df_drug_mapping = rgi_parser.get_drug_mapping(drug_classes)

    time_now = datetime.now()

    drug_mapping_subsets = {
        'all': df_drug_mapping,
        'day': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - timedelta(days=1))],
        'week': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - timedelta(days=7))],
        'month': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - timedelta(days=31))],
        'year': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - timedelta(days=365))],
    }

    # Set time dropdown text to include count of samples in particular time period
    # Should produce a dictionary like {'all': 'All (500)', ...}
    time_dropdown_text = {}
    all_drug_mapping_has_drugs = drug_mapping_subsets['all'][drug_mapping_subsets['all']['has_drugs']]
    time_dropdown_text['all'] = f'All ({len(all_drug_mapping_has_drugs)})'
    for label in ['day', 'week', 'month', 'year']:
        drug_mapping = drug_mapping_subsets[label]
        drug_mapping_matches = drug_mapping[drug_mapping['has_drugs']]
        time_dropdown_text[label] = f'Last {label} ({len(drug_mapping_matches)})'

    main_pane = figures.build_main_pane(drug_mapping_subsets[time_dropdown], rgi_parser, region_codes, data, world)

    time_period_options = [{'label': time_dropdown_text[x], 'value': x} for x in time_dropdown_text]

    return (main_pane,
            time_period_options)

if __name__ == '__main__':
    app.run_server(debug = True,
                  port = 8050,
                  host = '0.0.0.0')