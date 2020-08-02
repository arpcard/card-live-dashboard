from typing import List, Set, Dict
import pandas as pd
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State

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
    Output('rgi-parameters', 'is_open'),
    [Input('rgi-parameters-toggle', 'n_clicks')],
    [State('rgi-parameters', 'is_open')],
)
def toggle_rgi_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('time-parameters', 'is_open'),
    [Input('time-parameters-toggle', 'n_clicks')],
    [State('time-parameters', 'is_open')],
)
def toggle_time_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def apply_filters(data: CardLiveData, rgi_cutoff_select: str,
                  drug_classes: List[str], besthit_aro: List[str]) -> Dict[str, RGIParser]:
    time_now = datetime.now()

    rgi_parser = RGIParser(data.rgi_df) \
        .select(by='cutoff', type='row', level=rgi_cutoff_select) \
        .select(by='drug', type='file', drug_classes=drug_classes) \
        .select(by='aro', type='file', besthit_aro=besthit_aro)

    time_subsets = {
        'all': rgi_parser,
        'day': rgi_parser.select(by='time', type='row', start=time_now - DAY, end=time_now),
        'week': rgi_parser.select(by='time', type='row', start=time_now - WEEK, end=time_now),
        'month': rgi_parser.select(by='time', type='row', start=time_now - MONTH, end=time_now),
        'year': rgi_parser.select(by='time', type='row', start=time_now - YEAR, end=time_now),
    }

    return time_subsets


@app.callback(
    [Output('time-period-items', 'options'),
     Output('selected-samples-count', 'children'),
     Output('drug-class-select', 'options'),
     Output('besthit-aro-select', 'options'),
     Output('geographic-map-id', 'figure'),
     Output('timeline-id', 'figure'),
     Output('geographic-totals-id', 'figure'),
     Output('taxonomic-comparison-id', 'figure')],
    [Input('rgi-cutoff-select', 'value'),
     Input('drug-class-select', 'value'),
     Input('besthit-aro-select', 'value'),
     Input('time-period-items', 'value'),
     Input('timeline-type-select', 'value'),
     Input('timeline-color-select', 'value')]
)
def update_geo_time_figure(rgi_cutoff_select: str, drug_classes: List[str],
                           besthit_aro: List[str], time_dropdown: List[str],
                           timeline_type_select: str, timeline_color_select: str):
    """
    Main callback/controller for updating all figures based on user selections.
    :param rgi_cutoff_select: The selected RGI cutoff ('all' for all values).
    :param drug_classes: A list of the drug_classes to display.
    :param time_dropdown: The time selection.
    :param timeline_type_select: The selection for the timeline type.
    :return: The figures to place in the main figure region of the page.
    """
    data = CardLiveData.get_data_package()
    total_samples_count = len(data.main_df)

    time_subsets = apply_filters(data, rgi_cutoff_select, drug_classes, besthit_aro)

    fig_settings = {
        'timeline': {'type': timeline_type_select, 'color': timeline_color_select}
    }

    main_pane_figures = build_main_pane(time_subsets[time_dropdown], data, fig_settings)

    # Set time dropdown text to include count of samples in particular time period
    # Should produce a list of dictionaries like [{'label': 'All (500)', 'value': 'all'}, ...]
    time_dropdown_text = [{'label': f'All ({time_subsets["all"].count_files()})', 'value': 'all'}]
    for value in ['day', 'week', 'month', 'year']:
        time_dropdown_text.append({
            'label': f'Last {value} ({time_subsets[value].count_files()})',
            'value': value,
        })

    samples_count_string = f'{time_subsets[time_dropdown].count_files()}/{total_samples_count}'

    drug_class_options = build_options(drug_classes, time_subsets[time_dropdown].all_drugs())
    besthit_aro_options = build_options(besthit_aro, time_subsets[time_dropdown].all_besthit_aro())

    return (time_dropdown_text,
            samples_count_string,
            drug_class_options,
            besthit_aro_options,
            main_pane_figures['map'],
            main_pane_figures['timeline'],
            main_pane_figures['geographic_totals'],
            main_pane_figures['taxonomic_comparison'])


def build_options(selected_options: List[str], all_available_options: Set[str]):
    if selected_options is None or len(selected_options) == 0:
        selected_options_set = set()
    else:
        selected_options_set = set(selected_options)

    if all_available_options is None or len(all_available_options) == 0:
        all_available_options_set = set()
    else:
        all_available_options_set = all_available_options

    return [{'label': x, 'value': x} for x in sorted(
        all_available_options_set.union(selected_options_set))]


def build_main_pane(rgi_parser: RGIParser, data: CardLiveDataLoader, fig_settings: Dict[str, Dict[str,str]]):
    matches_count = rgi_parser.value_counts('geo_area_code').reset_index()
    matches_count = model.region_codes.add_region_standard_names(matches_count,
                                                                 region_column='geo_area_code')
    fig_map = figures.choropleth_drug(matches_count, model.world)

    df_rgi_kmer_subset = data.rgi_kmer_df.loc[rgi_parser.files()]
    df_lmat_subset = data.lmat_df.loc[rgi_parser.files()]
    tax_parse = TaxonomicParser(df_rgi_kmer_subset, df_lmat_subset)

    # Add all data to timeline dataframe for color_by option
    df_timeline = rgi_parser.data_by_file()
    if len(df_timeline) > 0:
        df_timeline = df_timeline.merge(tax_parse.create_file_matches(), left_index=True, right_index=True, how='left')
        df_timeline = model.region_codes.add_region_standard_names(df_timeline, 'geo_area_code')

    fig_histogram_rate = figures.build_time_histogram(df_timeline, fig_type=fig_settings['timeline']['type'],
                                                      color_by=fig_settings['timeline']['color'])
    fig_geographic_totals = figures.geographic_totals(matches_count)

    if rgi_parser.empty():
        fig_taxonomic_comparison = figures.taxonomic_comparison(pd.DataFrame())
    else:
        files_set = rgi_parser.files()
        df_rgi_kmer_subset = data.rgi_kmer_df.loc[files_set]
        df_lmat_subset = data.lmat_df.loc[files_set]
        tax_parse = TaxonomicParser(df_rgi_kmer_subset, df_lmat_subset)
        df_tax = tax_parse.create_rgi_lmat_both()

        fig_taxonomic_comparison = figures.taxonomic_comparison(df_tax)

    return {
        'map': fig_map,
        'timeline': fig_histogram_rate,
        'taxonomic_comparison': fig_taxonomic_comparison,
        'geographic_totals': fig_geographic_totals,
    }
