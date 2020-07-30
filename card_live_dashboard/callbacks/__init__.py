from typing import List
import pandas as pd
from datetime import datetime, timedelta
from dash.dependencies import Input, Output
import dash_core_components as dcc

from card_live_dashboard.app import app
from card_live_dashboard.model.RGIParser import RGIParser
from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.TaxonomicParser import TaxonomicParser
import card_live_dashboard.layouts.figures as figures
import card_live_dashboard.layouts as layouts
import card_live_dashboard.model as model

DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=31)
YEAR = timedelta(days=365)


@app.callback(
    [Output('main-pane', 'children'),
     Output('time-period-items', 'options')],
    [Input('drug-class-select', 'value'),
     Input('time-period-items', 'value')]
)
def update_geo_time_figure(drug_classes: List[str], time_dropdown):
    """
    Main callback/controller for updating all figures based on user selections.
    :param drug_classes: A list of the drug_classes to display.
    :param time_dropdown: The time selection.
    :return: The figures to place in the main figure region of the page.
    """
    data = CardLiveData.get_data_package()
    rgi_parser = RGIParser(data.rgi_df)
    df_drug_mapping = rgi_parser.get_drug_mapping(drug_classes)

    time_now = datetime.now()

    drug_mapping_subsets = {
        'all': df_drug_mapping,
        'day': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - DAY)],
        'week': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - WEEK)],
        'month': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - MONTH)],
        'year': df_drug_mapping[df_drug_mapping['timestamp'] >= (time_now - YEAR)],
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

    main_pane_figures = build_main_pane(drug_mapping_subsets[time_dropdown], rgi_parser, data)
    main_pane = layouts.figures_layout(main_pane_figures)

    time_period_options = [{'label': time_dropdown_text[x], 'value': x} for x in time_dropdown_text]

    return (main_pane,
            time_period_options)


def build_main_pane(df_drug_mapping: pd.DataFrame, rgi_parser: RGIParser, data: CardLiveDataLoader):
    geo_drug_classes_count = rgi_parser.geo_drug_sets_to_counts(df_drug_mapping).reset_index()
    geo_drug_classes_count = model.region_codes.add_region_standard_names(geo_drug_classes_count,
                                                                          region_column='geo_area_code')
    fig_map = figures.choropleth_drug(geo_drug_classes_count, model.world)
    fig_map.update_layout(transition_duration=500)

    df_drug_mapping = df_drug_mapping[df_drug_mapping['has_drugs']]

    fig_histogram_rate = figures.build_time_histogram(df_drug_mapping, cumulative=False)
    fig_histogram_rate.update_layout(transition_duration=500)

    files_subset = set(df_drug_mapping.index.tolist())
    df_rgi_kmer_subset = data.rgi_kmer_df.loc[files_subset]
    df_lmat_subset = data.lmat_df.loc[files_subset]
    tax_parse = TaxonomicParser(df_rgi_kmer_subset, df_lmat_subset)
    df_tax = tax_parse.create_rgi_lmat_both()

    fig_taxonomic_comparison = figures.taxonomic_comparison(df_tax)

    return {
        'map': fig_map,
        'timeline': fig_histogram_rate,
        'taxonomic_comparison': fig_taxonomic_comparison,
    }
