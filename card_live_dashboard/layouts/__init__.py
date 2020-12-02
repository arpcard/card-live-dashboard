from datetime import datetime
from typing import Dict, List, Union

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

import card_live_dashboard
import card_live_dashboard.layouts.figures as figures

external_stylesheets = [dbc.themes.BOOTSTRAP]

LOADING = '[LOADING]'


def default_layout(base_pathname='/'):
    """
    Builds the default layout of the CARD:Live dashboard.
    :param base_pathname: The base pathname where the CARD:Live application is running.
    :return: The default layout of the CARD:Live dashboard.
    """
    if base_pathname.endswith('/'):
        base_pathname = base_pathname.rstrip('/')

    layout = html.Div(className='card-live-all container-fluid', children=[
        html.Div(className='row', children=[
            html.Div(className='card-live-panel col-lg-3', children=[
                html.Div(className='sticky-top', children=[
                    html.H1([
                        'CARD:Live'
                    ]),
                    html.Div(className='pt-2 pb-1', children=[
                        'Welcome to the ',
                        html.A(children=['CARD:Live'], href='https://card.mcmaster.ca/live'),
                        ' dashboard. This provides summaries of detected antimicrobial resistance for user-submitted',
                        ' genomic samples to the online ',
                        html.A(children=['RGI tool'], href='https://card.mcmaster.ca/analyze/rgi'),
                        '.',
                    ]),
                    html.Div(className='card-live-badges pb-3', children=[
                        html.Span(className='badge badge-secondary', children=[
                            html.Span(id='global-sample-count', children=[LOADING]),
                            ' samples']),
                        ' ',
                        html.Span(className='badge badge-secondary',
                                  children=['Most recent: ', html.Span(id='global-most-recent', children=[LOADING])]),
                        ' ',
                        html.A(className='badge badge-primary', href=f'{base_pathname}/data/all',
                               children=['Download results'])
                    ]),
                    html.Div([
                        html.H2('Selection criteria'),
                        html.P([
                            'Please select from the options below to examine subsets of the samples.',
                            html.Div(className='card-live-badges pt-1', children=[
                                html.Span(className='badge badge-secondary', children=[
                                    'Showing ', html.Span(id='selected-samples-count',
                                                          children=[LOADING]),
                                    ' samples'
                                ]),
                            ]),
                        ]),
                    ]),
                    html.Div([
                        dbc.Button(id='rgi-parameters-toggle', color='link',
                                   className='cardlive-collapse pl-0', children=[
                                html.H3(className='sidebar-title', children=['RGI']),
                                html.Span(className='sidebar-description', children=['Filter by RGI results']),
                            ]),
                        dbc.Collapse(id='rgi-parameters', is_open=True, children=[
                            html.Div(children=['RGI results cutoff: ',
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
                            html.Div(children=['Filter samples by drug class: ',
                                               dcc.Dropdown(
                                                   id='drug-class-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select a drug class',
                                               ),
                                               ]),
                            html.Div(children=['Filter samples by AMR gene family: ',
                                               dcc.Dropdown(
                                                   id='amr-gene-family-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select the AMR gene family',
                                               ),
                                               ]),
                            html.Div(children=['Filter samples by resistance mechanism: ',
                                               dcc.Dropdown(
                                                   id='resistance-mechanism-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select the resistance mechanism',
                                               ),
                                               ]),
                            html.Div(children=['Filter samples by AMR gene: ',
                                               dcc.Dropdown(
                                                   id='amr-gene-select',
                                                   className='sidepanel-selection',
                                                   multi=True,
                                                   placeholder='Select an AMR gene',
                                               ),
                                               ]),
                        ]),
                    ]),
                    html.Div([
                        dbc.Button(id='organism-parameters-toggle', color='link',
                                   className='cardlive-collapse pl-0', children=[
                                html.H3(className='sidebar-title', children=['Organism']),
                                html.Span(className='sidebar-description', children=['Filter by organism']),
                            ]),
                        dbc.Collapse(id='organism-parameters', is_open=True, children=[
                            html.Div(children=['Organism identification method: ',
                                               dbc.RadioItems(
                                                   id='organism-identification-method',
                                                   className='sidepanel-selection-light',
                                                   options=[
                                                       {'label': 'LMAT', 'value': 'lmat'},
                                                       {'label': 'RGI Kmer', 'value': 'rgi_kmer'},
                                                   ],
                                                   value='lmat',
                                                   inline=True,
                                               ),
                                               ]),
                            html.Div(children=['Select an organism: ',
                                               dcc.Dropdown(id='organism-select',
                                                            className='sidepanel-selection',
                                                            placeholder='Organism',
                                                            clearable=True)
                                               ]),
                        ]),
                    ]),
                    html.Div([
                        dbc.Button(id='time-parameters-toggle', color='link',
                                   className='cardlive-collapse pl-0', children=[
                                html.H3(className='sidebar-title', children=['Time']),
                                html.Span(className='sidebar-description', children=['Filter by submission time']),
                            ]),
                        dbc.Collapse(id='time-parameters', is_open=True, children=[
                            html.Div(children=['Filter by submission time period: ',
                                               dcc.Dropdown(id='time-period-items',
                                                            className='sidepanel-selection',
                                                            value='all',
                                                            clearable=False),
                                               dbc.Collapse(id='custom-time-period', is_open=False, children=[
                                                   'Please select a custom date range:',
                                                   dcc.DatePickerRange(
                                                       id='date-picker-range',
                                                       className='sidepanel-selection',
                                                       display_format='MMM DD, YYYY',
                                                       min_date_allowed=datetime(2020, 1, 1),
                                                       max_date_allowed=datetime.now(),
                                                       updatemode='bothdates',
                                                       end_date=datetime.now(),
                                                       with_portal=True,
                                                       clearable=True,
                                                       number_of_months_shown=2,
                                                   ),
                                               ])
                                               ]),
                        ]),
                    ]),
                    html.P(className='text-center card-live-badges pb-5', children=[
                        html.Br(),
                        html.A(className='badge badge-primary my-1',
                               children=[f'Version | {card_live_dashboard.__version__}'],
                               href='https://github.com/arpcard/card-live-dashboard/releases'),
                        html.Br(),
                        html.A(className='badge badge-primary my-1',
                               children=['Code and Docs | GitHub'],
                               href='https://github.com/arpcard/card-live-dashboard')
                    ]),
                    html.Div(className='py-5')
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
            single_figure_layout(title='Map',
                                 description=['Geographic distribution of the submitted genomic samples.'],
                                 id='figure-geographic-map-id',
                                 fig=figures_dict['map']
                                 ),
            single_figure_layout(title='Samples timeline',
                                 description=['Submission dates for genomic samples.'],
                                 id='figure-timeline-id',
                                 fig=figures_dict['timeline'],
                                 dropdowns=figure_menus_layout(
                                     id_type='timeline-type-select',
                                     options_type=[
                                         {'label': 'Cumulative counts', 'value': 'cumulative_counts'},
                                         {'label': 'Cumulative percent', 'value': 'cumulative_percent'},
                                         {'label': 'Counts', 'value': 'counts'},
                                         {'label': 'Percent', 'value': 'percent'},
                                     ],
                                     value_type='cumulative_counts',
                                     id_color='timeline-color-select',
                                     options_color=[
                                         {'label': 'Default', 'value': 'default'},
                                         {'label': 'Geographic region', 'value': 'geographic'},
                                         {'label': 'Organism', 'value': 'organism'},
                                     ],
                                     value_color='default'
                                 ),
                                 ),
            single_figure_layout(title='Samples total',
                                 description=['Count of samples matching selection.'],
                                 id='figure-totals-id',
                                 fig=figures_dict['totals'],
                                 dropdowns=figure_menus_layout(
                                     id_type='totals-type-select',
                                     options_type=[
                                         {'label': 'Geographic region', 'value': 'geographic'},
                                         {'label': 'Organism', 'value': 'organism'},
                                     ],
                                     value_type='geographic',
                                     id_color='totals-color-select',
                                     options_color=[
                                         {'label': 'Default', 'value': 'default'},
                                         {'label': 'Geographic region', 'value': 'geographic'},
                                         {'label': 'Organism', 'value': 'organism'},
                                     ],
                                     value_color='default'
                                 ),
                                 ),
            single_figure_layout(title='RGI results',
                                 description=['Percent of selected samples (',
                                              html.Span(id='sample-count-figure', children=[LOADING]),
                                              ') with the chosen type of RGI results.'
                                              ],
                                 id='figure-rgi-id',
                                 fig=figures_dict['rgi'],
                                 dropdowns=figure_menus_layout(
                                     id_type='rgi-type-select',
                                     options_type=[
                                         {'label': 'Drug class', 'value': 'drug_class'},
                                         {'label': 'AMR gene', 'value': 'amr_gene'},
                                         {'label': 'AMR gene family', 'value': 'amr_gene_family'},
                                         {'label': 'Resistance mechanism', 'value': 'resistance_mechanism'},
                                     ],
                                     value_type='drug_class',
                                     id_color='rgi-color-select',
                                     options_color=[
                                         {'label': 'Default', 'value': 'default'},
                                         {'label': 'Geographic region', 'value': 'geographic'},
                                         {'label': 'Organism', 'value': 'organism'},
                                     ],
                                     value_color='default'
                                 ),
                                 ),
        ])
    ]


def single_figure_layout(title: str, description: List[Union[str, html.Span]], id: str, fig: go.Figure,
                         dropdowns: html.Div = None):
    component = dbc.Card(className='my-3', children=[
        dbc.CardHeader(children=[
            html.H4(className='figure-title', children=[title]),
            html.Span(className='figure-description', children=description),
            dropdowns,
        ]),
        dcc.Loading(type='circle', children=[
            dbc.CardBody(children=[
                dcc.Graph(id=id, figure=fig),
            ]),
        ]),
    ])

    return component


def figure_menus_layout(id_type: str, options_type: List[Dict[str, str]], value_type: str,
                        id_color: str = None, options_color: List[Dict[str, str]] = None,
                        value_color: str = None) -> html.Div:
    elements = [html.Div(['Type:']), html.Div(className='ml-2', children=[dcc.Dropdown(
        id=id_type,
        options=options_type,
        searchable=False,
        clearable=False,
        value=value_type,
    )])]

    if id_color is not None:
        elements.append(html.Div(className='ml-3', children=['Color by:']))
        elements.append(html.Div(className='ml-2', children=[dcc.Dropdown(
            id=id_color,
            options=options_color,
            searchable=False,
            clearable=False,
            value=value_color,
        )]))

    return html.Div(className='d-flex align-items-center', children=elements)
