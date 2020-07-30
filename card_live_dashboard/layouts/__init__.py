from typing import Dict

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser

external_stylesheets = [dbc.themes.BOOTSTRAP]


def default_layout():
    """
    Builds the default layout of the CARD:Live dashboard.
    :return: The default layout of the CARD:Live dashboard.
    """
    data = CardLiveData.get_data_package()
    rgi_parser = RGIParser(data.rgi_df)
    all_drugs = rgi_parser.all_drugs_list()

    number_of_samples = len(data.main_df)
    last_updated = data.main_df['timestamp'].max()

    layout = html.Div(className='card-live-all container-fluid', children=[
        html.Div(className='row', children=[
            html.Div(className='card-live-panel col-sm-3', children=[
                html.Div(className='sticky-top', children=[
                    html.H1([
                        'CARD:Live'
                    ]),
                    html.Div(className='pt-2 pb-1', children=[
                        'Welcome to the ',
                        html.A(children=['CARD:Live'], href='https://card.mcmaster.ca/live'),
                        ' dashboard. Please select from the options below to examine subsets of the ',
                        html.A(children=['CARD:Live'], href='https://card.mcmaster.ca/live'),
                        ' data.',
                    ]),
                    html.Div(className='card-live-badges pb-3', children=[
                        html.Span(className='badge badge-secondary', children=[f'{number_of_samples} samples']),
                        ' ',
                        html.Span(className='badge badge-secondary',
                                  children=[f'Updated: {last_updated: %b %d, %Y}']),
                    ]),
                    html.H2('RGI'),
                    html.Div(children=['RGI cutoff: ',
                                       dcc.Dropdown(
                                           id='rgi-cutoff',
                                           options=[
                                               {'label': 'Perfect', 'value': 'perfect'},
                                               {'label': 'Strict', 'value': 'strict'},
                                               {'label': 'Loose', 'value': 'loose'},
                                           ],
                                           multi=True,
                                           placeholder='Select an RGI cutoff',
                                       ),
                                       ]),
                    html.Div(children=['Filter display by drug class: ',
                                       dcc.Dropdown(
                                           id='drug-class-select',
                                           options=[{'label': x, 'value': x} for x in all_drugs],
                                           multi=True,
                                           placeholder='Select a drug class',
                                       ),
                                       ]),
                    html.H2('Time'),
                    html.Div(children=['Select a time period: ',
                                       dcc.Dropdown(id='time-period-items',
                                                    value='all',
                                                    clearable=False)
                                       ]),
                    html.P(className='text-center card-live-badges', children=[
                        html.Br(),
                        html.A(className='badge badge-primary', children=['Code | GitLab'],
                               href='https://devcard.mcmaster.ca:8888/apetkau/card-live-dashboard'),
                    ]),
                ]),
            ]),
            html.Div(className='col', children=[
                dcc.Loading(children=[
                    html.Div(className='container', children=[
                        html.Div(className='row', children=[html.Div(className='col', id='main-pane')]),
                    ])
                ]),
            ])
        ]),
    ])

    return layout


def figures_layout(figures_dict: Dict[str, go.Figure]):
    """
    Builds the layout of the figures on the page.
    :param figures_dict: A dictionary mapping names of constructed figures to the figure objects.
    :return: A list of figures to place on the page.
    """
    return [
        html.Div([
            'This shows a world map of the distribution of samples uploaded to CARD:Live matching the selected criteria.',
            dcc.Graph(figure=figures_dict['map']),
            dcc.Graph(figure=figures_dict['timeline']),
            dcc.Graph(figure=figures_dict['taxonomic_comparison']),
        ])
    ]
