from typing import Dict

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

import card_live_dashboard.layouts.figures as figures
from card_live_dashboard.model.CardLiveData import CardLiveData

external_stylesheets = [dbc.themes.BOOTSTRAP]


def default_layout():
    """
    Builds the default layout of the CARD:Live dashboard.
    :return: The default layout of the CARD:Live dashboard.
    """
    data = CardLiveData.get_data_package()
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
                        ' dashboard.'
                    ]),
                    html.Div(className='card-live-badges pb-3', children=[
                        html.Span(className='badge badge-secondary', children=[f'{number_of_samples} samples']),
                        ' ',
                        html.Span(className='badge badge-secondary',
                                  children=[f'Updated: {last_updated: %b %d, %Y}']),
                    ]),
                    html.Div([
                        html.H2('Selection criteria'),
                        html.P([
                            'Please select from the options below to examine subsets of the ',
                            html.A(children=['CARD:Live'], href='https://card.mcmaster.ca/live'),
                            ' data.',
                            html.Div(className='card-live-badges pt-1', children=[
                                html.Span(className='badge badge-secondary', children=[
                                    'Showing ', html.Span(id='selected-samples-count',
                                                          children=[f'{number_of_samples}/{number_of_samples}']),
                                    ' samples'
                                ]),
                            ]),
                        ]),
                    ]),
                    html.Div([
                        dbc.Button(id='rgi-parameters-toggle', color='link',
                                   className='cardlive-collapse pl-0', children=[html.H3('RGI')]),
                        dbc.Collapse(id='rgi-parameters', is_open=True, children=[
                            html.Div(children=['RGI cutoff: ',
                                               dbc.RadioItems(
                                                   id='rgi-cutoff-select',
                                                   className='sidepanel-selection-light',
                                                   options=[
                                                       {'label': 'All', 'value': 'all'},
                                                       {'label': 'Perfect', 'value': 'perfect'},
                                                       {'label': 'Strict', 'value': 'strict'},
                                                   ],
                                                   value='all',
                                                   inline=True,
                                               ),
                            ]),
                            html.Div(children=['Filter display by drug class: ',
                                               dcc.Dropdown(
                                                   id='drug-class-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select a drug class',
                                               ),
                            ]),
                            html.Div(children=['Filter display by Best Hit ARO: ',
                                               dcc.Dropdown(
                                                   id='besthit-aro-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select a Best Hit ARO value',
                                               ),
                            ]),
                        ]),
                    ]),
                    html.Div([
                        dbc.Button(id='time-parameters-toggle', color='link',
                                   className='cardlive-collapse pl-0', children=[html.H3('Time')]),
                        dbc.Collapse(id='time-parameters', is_open=True, children=[
                            html.Div(children=['Select a time period: ',
                                               dcc.Dropdown(id='time-period-items',
                                                            className='sidepanel-selection',
                                                            value='all',
                                                            clearable=False)
                           ]),
                        ]),
                    ]),
                    html.P(className='text-center card-live-badges', children=[
                        html.Br(),
                        html.A(className='badge badge-primary', children=['Code | GitLab'],
                               href='https://devcard.mcmaster.ca:8888/apetkau/card-live-dashboard'),
                    ]),
                ]),
            ]),
            html.Div(className='col', children=[
                html.Div(className='container', children=[
                    html.Div(className='row', children=[
                        html.Div(className='col', id='main-pane',
                            # Need to display initial empty figures
                            # So callbacks can be linked up correctly
                            children=figures_layout(figures.EMPTY_FIGURE_DICT)
                        ),
                    ]),
                ]),
            ]),
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
        html.Div(className='cardlive-figures', children=[
            single_figure_layout(title='Geographic map',
                                 id='geographic-map-id',
                                 fig=figures_dict['map']
            ),
            single_figure_layout(title='Geographic totals',
                                 id='geographic-totals-id',
                                 fig=figures_dict['geographic_totals']
            ),
            single_figure_layout(title='Timeline',
                                 id='timeline-id',
                                 fig=figures_dict['timeline'],
                                 dropdowns=html.Div(className='d-flex align-items-center', children=[
                                      html.Div(['Type:']),
                                      html.Div(className='flex-grow-1 ml-2', children=[dcc.Dropdown(
                                          id='timeline-type-select',
                                          options=[
                                              {'label': 'Rate', 'value': 'rate'},
                                              {'label': 'Cumulative', 'value': 'cumulative'}
                                          ],
                                          searchable=False,
                                          clearable=False,
                                          value='rate',
                                      )]),
                                 ]),
            ),
            single_figure_layout(title='Taxonomic comparison',
                                 id='taxonomic-comparison-id',
                                 fig=figures_dict['taxonomic_comparison']
            ),
        ])
    ]


def single_figure_layout(title: str, id: str, fig: go.Figure, dropdowns: html.Div = None):
    component = dbc.Card(className='my-3', children=[
        dbc.CardHeader(children=[
            html.H4(title),
            dropdowns,
        ]),
        dcc.Loading(type='circle', children=[
            dbc.CardBody(children=[
                        dcc.Graph(id=id, figure=fig),
            ]),
        ]),
    ])

    return component