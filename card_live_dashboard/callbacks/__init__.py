from typing import List
from datetime import datetime, timedelta
from dash.dependencies import Input, Output

from card_live_dashboard.app import app
from card_live_dashboard.model.RGIParser import RGIParser
from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
import card_live_dashboard.layouts.figures as figures

rgi_parser: RGIParser = None
data: CardLiveDataLoader = None

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

    main_pane = figures.build_main_pane(drug_mapping_subsets[time_dropdown], rgi_parser, data)

    time_period_options = [{'label': time_dropdown_text[x], 'value': x} for x in time_dropdown_text]

    return (main_pane,
            time_period_options)
