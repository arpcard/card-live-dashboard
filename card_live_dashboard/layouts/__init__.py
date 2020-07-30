from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser

side_panel_section_style = {
    'padding': '10px'
}

external_stylesheets = [dbc.themes.BOOTSTRAP]

def default_layout():
    data = CardLiveData.get_data_package()
    rgi_parser = RGIParser(data.rgi_df)
    all_drugs = rgi_parser.all_drugs_list()

    number_of_samples = len(data.main_df)
    last_updated = data.main_df['timestamp'].max()

    layout = html.Div(className='container-fluid', children=[
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
                        html.A(className='badge badge-primary', children=['Code | GitLab'],
                               href='https://devcard.mcmaster.ca:8888/apetkau/amr-visualization-summer-2020'),
                    ]),
                ]),
            ], style={'background-color': '#2c3e50', 'color': 'white'}),
            html.Div(className='col', children=[
                dcc.Loading(children=[
                    html.Div(className='container', children=[
                        html.Div(className='row', children=[html.Div(className='col', id='main-pane')]),
                    ])
                ]),
            ], style={'background-color': 'white'})
        ]),
    ], style={'background-color': '##2c3e50'})

    return layout
