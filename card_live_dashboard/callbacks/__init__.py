from typing import List, Set, Dict
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import dash

from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.TaxonomicParser import TaxonomicParser
import card_live_dashboard.layouts.figures as figures
import card_live_dashboard.model as model

DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=31)
YEAR = timedelta(days=365)


def build_callbacks(app: dash.dash.Dash) -> None:
    """
    Builds and sets up all callbacks for the passed dash app.
    :param app: The Dash app to setup callbacks for.
    :return: None.
    """

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

    @app.callback(
        [Output('global-sample-count', 'children'),
         Output('global-most-recent', 'children'),
         Output('time-period-items', 'options'),
         Output('selected-samples-count', 'children'),
         Output('drug-class-select', 'options'),
         Output('besthit-aro-select', 'options'),
         Output('figure-geographic-map-id', 'figure'),
         Output('figure-timeline-id', 'figure'),
         Output('figure-totals-id', 'figure')],
        [Input('rgi-cutoff-select', 'value'),
         Input('drug-class-select', 'value'),
         Input('besthit-aro-select', 'value'),
         Input('time-period-items', 'value'),
         Input('timeline-type-select', 'value'),
         Input('timeline-color-select', 'value'),
         Input('totals-type-select', 'value'),
         Input('totals-color-select', 'value'),
         Input('auto-update-interval', 'n_intervals')]
    )
    def update_all_figures(rgi_cutoff_select: str, drug_classes: List[str],
                           besthit_aro: List[str], time_dropdown: str,
                           timeline_type_select: str, timeline_color_select: str,
                           totals_type_select: str, totals_color_select: str,
                           n_intervals):
        """
        Main callback/controller for updating all figures based on user selections.
        :param rgi_cutoff_select: The selected RGI cutoff ('all' for all values).
        :param drug_classes: A list of the drug_classes to display.
        :param besthit_aro: The list of best hit ARO values to select by.
        :param time_dropdown: The time selection.
        :param timeline_type_select: The selection for the timeline type.
        :param timeline_color_select: The color selection for the timeline.
        :return: The figures to place in the main figure region of the page.
        """
        data = CardLiveDataManager.get_instance().card_data
        global_samples_count = len(data)
        global_last_updated = f'{data.latest_update(): %b %d, %Y}'

        time_subsets = apply_filters(data, rgi_cutoff_select, drug_classes, besthit_aro)

        fig_settings = {
            'timeline': {'type': timeline_type_select, 'color': timeline_color_select},
            'totals': {'type': totals_type_select, 'color': totals_color_select}
        }

        main_pane_figures = build_main_pane(time_subsets[time_dropdown], fig_settings)

        # Set time dropdown text to include count of samples in particular time period
        # Should produce a list of dictionaries like [{'label': 'All (500)', 'value': 'all'}, ...]
        time_dropdown_text = [{'label': f'All ({time_subsets["all"].samples_count()})', 'value': 'all'}]
        for value in ['day', 'week', 'month', 'year']:
            time_dropdown_text.append({
                'label': f'Last {value} ({time_subsets[value].samples_count()})',
                'value': value,
            })

        samples_count_string = f'{time_subsets[time_dropdown].samples_count()}/{global_samples_count}'

        drug_class_options = build_options(drug_classes, time_subsets[time_dropdown].rgi_parser.all_drugs())
        besthit_aro_options = build_options(besthit_aro, time_subsets[time_dropdown].rgi_parser.all_besthit_aro())

        return (global_samples_count,
                global_last_updated,
                time_dropdown_text,
                samples_count_string,
                drug_class_options,
                besthit_aro_options,
                main_pane_figures['map'],
                main_pane_figures['timeline'],
                main_pane_figures['totals'])


def apply_filters(data: CardLiveData, rgi_cutoff_select: str,
                  drug_classes: List[str], besthit_aro: List[str]) -> Dict[str, CardLiveData]:
    time_now = datetime.now()

    data = data.select(table='rgi', by='cutoff', type='row', level=rgi_cutoff_select) \
        .select(table='rgi', by='drug', type='file', drug_classes=drug_classes) \
        .select(table='rgi', by='aro', type='file', besthit_aro=besthit_aro)

    time_subsets = {
        'all': data,
        'day': data.select(table='main', by='time', start=time_now - DAY, end=time_now),
        'week': data.select(table='main', by='time', start=time_now - WEEK, end=time_now),
        'month': data.select(table='main', by='time', start=time_now - MONTH, end=time_now),
        'year': data.select(table='main', by='time', start=time_now - YEAR, end=time_now),
    }

    return time_subsets


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


def build_main_pane(data: CardLiveData, fig_settings: Dict[str, Dict[str, str]]):
    geographic_counts = data.value_counts(['geo_area_code']).reset_index()
    geographic_counts = model.region_codes.add_region_standard_names(geographic_counts,
                                                                     region_column='geo_area_code')
    fig_map = figures.choropleth_drug(geographic_counts, model.world)
    tax_parse = TaxonomicParser(data.rgi_kmer_df, data.lmat_df)

    # Add all data to timeline dataframe for color_by option
    df_timeline = data.rgi_parser.data_by_file()
    if len(df_timeline) > 0:
        df_timeline = df_timeline.merge(tax_parse.create_file_matches(), left_index=True, right_index=True,
                                        how='left')
        df_timeline = model.region_codes.add_region_standard_names(df_timeline, 'geo_area_code')

    fig_histogram_rate = figures.build_time_histogram(df_timeline, fig_type=fig_settings['timeline']['type'],
                                                      color_by=fig_settings['timeline']['color'])

    fig_totals = figures.totals_figure(data, tax_parse, type_value=fig_settings['totals']['type'],
                                       color_by_value=fig_settings['totals']['color'])

    return {
        'map': fig_map,
        'timeline': fig_histogram_rate,
        'totals': fig_totals,
    }
