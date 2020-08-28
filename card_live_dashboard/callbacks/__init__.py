from typing import List, Set, Dict
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import dash
import re

from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
from card_live_dashboard.model.CardLiveData import CardLiveData
import card_live_dashboard.layouts.figures as figures
from card_live_dashboard.model import world

DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=31)
THREE_MONTHS = timedelta(days=365 / 4)  # 3 months is defined as a quarter year
SIX_MONTHS = timedelta(days=365 / 2)  # 6 months is defined as half a year
YEAR = timedelta(days=365)

ORGANISM_COLUMN = {
    'lmat': 'lmat_taxonomy',
    'rgi_kmer': 'rgi_kmer_taxonomy',
}


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
        Output('organism-parameters', 'is_open'),
        [Input('organism-parameters-toggle', 'n_clicks')],
        [State('organism-parameters', 'is_open')],
    )
    def toggle_organism_parameters_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output('custom-time-period', 'is_open'),
        [Input('time-period-items', 'value')]
    )
    def toggle_custom_time_period(time_period_items):
        return time_period_items == 'custom'

    @app.callback(
        [Output('global-sample-count', 'children'),
         Output('global-most-recent', 'children'),
         Output('time-period-items', 'options'),
         Output('date-picker-range', 'min_date_allowed'),
         Output('date-picker-range', 'max_date_allowed'),
         Output('organism-select', 'options'),
         Output('selected-samples-count', 'children'),
         Output('drug-class-select', 'options'),
         Output('amr-gene-family-select', 'options'),
         Output('resistance-mechanism-select', 'options'),
         Output('amr-gene-select', 'options'),
         Output('figure-geographic-map-id', 'figure'),
         Output('figure-timeline-id', 'figure'),
         Output('figure-totals-id', 'figure'),
         Output('figure-rgi-id', 'figure')],
        [Input('rgi-cutoff-select', 'value'),
         Input('drug-class-select', 'value'),
         Input('amr-gene-family-select', 'value'),
         Input('resistance-mechanism-select', 'value'),
         Input('amr-gene-select', 'value'),
         Input('organism-identification-method', 'value'),
         Input('organism-select', 'value'),
         Input('time-period-items', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('timeline-type-select', 'value'),
         Input('timeline-color-select', 'value'),
         Input('totals-type-select', 'value'),
         Input('totals-color-select', 'value'),
         Input('rgi-type-select', 'value'),
         Input('auto-update-interval', 'n_intervals')]
    )
    def update_all_figures(rgi_cutoff_select: str, drug_classes: List[str],
                           amr_gene_families: List[str], resistance_mechanisms: List[str],
                           amr_genes: List[str], organism_identification_method: str, organism: str,
                           time_dropdown: str, start_date: str, end_date: str,
                           timeline_type_select: str, timeline_color_select: str,
                           totals_type_select: str, totals_color_select: str,
                           rgi_type_select: str, n_intervals):
        """
        Main callback/controller for updating all figures based on user selections.
        :param rgi_cutoff_select: The selected RGI cutoff ('all' for all values).
        :param drug_classes: A list of the drug_classes to display.
        :param amr_genes: The list of AMR genes (best hit ARO values) to select by.
        :param time_dropdown: The time selection.
        :param timeline_type_select: The selection for the timeline type.
        :param timeline_color_select: The color selection for the timeline.
        :return: The figures to place in the main figure region of the page.
        """
        data = CardLiveDataManager.get_instance().card_data
        global_samples_count = len(data)
        global_last_updated = f'{data.latest_update(): %b %d, %Y}'

        min_date_allowed = data.first_update()
        max_date_allowed = datetime.now()

        custom_date = {
            'start': min_date_allowed,
            'end': max_date_allowed
        }

        if start_date is not None:
            start_date = datetime.strptime(re.split(r'[T ]', start_date)[0], '%Y-%m-%d')
            custom_date['start'] = start_date
        if end_date is not None:
            end_date = datetime.strptime(re.split(r'[T ]', end_date)[0], '%Y-%m-%d')
            custom_date['end'] = end_date

        time_subsets = apply_filters(data=data,
                                     rgi_cutoff_select=rgi_cutoff_select,
                                     drug_classes=drug_classes,
                                     amr_gene_families=amr_gene_families,
                                     resistance_mechanisms=resistance_mechanisms,
                                     amr_genes=amr_genes,
                                     custom_date=custom_date)

        # I have to extract the list of available organism options prior to filtering the data by the selected organism
        # Otherwise once a user selects an organism there will be no other options available
        organism_column = ORGANISM_COLUMN[organism_identification_method]
        organism_options = build_options([organism],
                                         time_subsets[time_dropdown].unique_column(organism_column))

        time_subsets = apply_organism_filter(time_subsets=time_subsets,
                                             organism_identification_method=organism_identification_method,
                                             organism=organism)

        fig_settings = build_fig_settings(timeline_type_select=timeline_type_select,
                                          timeline_color_select=timeline_color_select,
                                          totals_type_select=totals_type_select,
                                          totals_color_select=totals_color_select,
                                          rgi_type_select=rgi_type_select,
                                          organism_identification_method=organism_identification_method
                                          )

        main_pane_figures = build_main_pane(time_subsets[time_dropdown], organism_identification_method, fig_settings)

        # Set time dropdown text to include count of samples in particular time period
        # Should produce a list of dictionaries like [{'label': 'All (500)', 'value': 'all'}, ...]
        time_dropdown_text = [{'label': f'All ({time_subsets["all"].samples_count()})', 'value': 'all'}]
        for value in ['day', 'week', 'month', '3 months', '6 months', 'year']:
            time_dropdown_text.append({
                'label': f'Last {value} ({time_subsets[value].samples_count()})',
                'value': value,
            })
        time_dropdown_text.append({'label': 'Custom', 'value': 'custom'})

        samples_count_string = f'{time_subsets[time_dropdown].samples_count()}/{global_samples_count}'

        drug_class_options = build_options(drug_classes,
                                           time_subsets[time_dropdown].rgi_parser.all_drugs())
        amr_gene_families_options = build_options(amr_gene_families,
                                                  time_subsets[time_dropdown].rgi_parser.all_amr_gene_family())
        resistance_mechanisms_options = build_options(resistance_mechanisms,
                                                      time_subsets[
                                                          time_dropdown].rgi_parser.all_resistance_mechanisms())
        amr_gene_options = build_options(amr_genes,
                                         time_subsets[time_dropdown].rgi_parser.all_amr_genes())

        return (global_samples_count,
                global_last_updated,
                time_dropdown_text,
                min_date_allowed,
                max_date_allowed,
                organism_options,
                samples_count_string,
                drug_class_options,
                amr_gene_families_options,
                resistance_mechanisms_options,
                amr_gene_options,
                main_pane_figures['map'],
                main_pane_figures['timeline'],
                main_pane_figures['totals'],
                main_pane_figures['rgi'])


def build_fig_settings(timeline_type_select: str, timeline_color_select: str, totals_type_select: str,
                       totals_color_select: str, rgi_type_select: str,
                       organism_identification_method: str) -> Dict[str, Dict[str, str]]:
    if timeline_color_select == 'organism':
        timeline_color_select = f'{timeline_color_select}_{organism_identification_method}'
    if totals_type_select == 'organism':
        totals_type_select = f'{totals_type_select}_{organism_identification_method}'
    if totals_color_select == 'organism':
        totals_color_select = f'{totals_color_select}_{organism_identification_method}'

    fig_settings = {
        'timeline': {'type': timeline_type_select, 'color': timeline_color_select},
        'totals': {'type': totals_type_select, 'color': totals_color_select},
        'rgi': {'type': rgi_type_select}
    }

    return fig_settings


def apply_filters(data: CardLiveData, rgi_cutoff_select: str,
                  drug_classes: List[str], amr_gene_families: List[str],
                  resistance_mechanisms: List[str], amr_genes: List[str],
                  custom_date: Dict[str, datetime]) -> Dict[str, CardLiveData]:
    time_now = datetime.now()

    data = data.select(table='rgi', by='cutoff', type='row', level=rgi_cutoff_select) \
        .select(table='rgi', by='drug', type='file', elements=drug_classes) \
        .select(table='rgi', by='amr_gene_family', type='file', elements=amr_gene_families) \
        .select(table='rgi', by='resistance_mechanism', type='file', elements=resistance_mechanisms) \
        .select(table='rgi', by='amr_gene', type='file', elements=amr_genes)

    time_subsets = {
        'all': data,
        'day': data.select(table='main', by='time', start=time_now - DAY, end=time_now),
        'week': data.select(table='main', by='time', start=time_now - WEEK, end=time_now),
        'month': data.select(table='main', by='time', start=time_now - MONTH, end=time_now),
        '3 months': data.select(table='main', by='time', start=time_now - THREE_MONTHS, end=time_now),
        '6 months': data.select(table='main', by='time', start=time_now - SIX_MONTHS, end=time_now),
        'year': data.select(table='main', by='time', start=time_now - YEAR, end=time_now),
    }

    if custom_date is not None:
        time_subsets['custom'] = data.select(table='main', by='time', start=custom_date['start'],
                                             end=custom_date['end'])
    else:
        time_subsets['custom'] = data

    return time_subsets


def apply_organism_filter(time_subsets: Dict[str, CardLiveData],
                          organism_identification_method: str, organism: str) -> Dict[str, CardLiveData]:
    time_subsets_filtered = {}
    for key in time_subsets:
        time_subsets_filtered[key] = time_subsets[key].select(
            table='main', by=ORGANISM_COLUMN[organism_identification_method], taxonomy=organism)

    return time_subsets_filtered

def build_options(selected_options: List[str], all_available_options: Set[str]):
    if selected_options is None or len(selected_options) == 0:
        selected_options_set = set()
    elif len(selected_options) == 1 and selected_options[0] == None:
        selected_options_set = set()
    else:
        selected_options_set = set(selected_options)

    if all_available_options is None or len(all_available_options) == 0:
        all_available_options_set = set()
    else:
        all_available_options_set = all_available_options

    return [{'label': x, 'value': x} for x in sorted(
        all_available_options_set.union(selected_options_set))]


def build_main_pane(data: CardLiveData, organism_identification_method: str, fig_settings: Dict[str, Dict[str, str]]):
    fig_map = figures.choropleth_drug(data, world)
    fig_histogram_rate = figures.build_time_histogram(data, fig_type=fig_settings['timeline']['type'],
                                                      color_by=fig_settings['timeline']['color'])
    fig_totals = figures.totals_figure(data, type_value=fig_settings['totals']['type'],
                                       color_by_value=fig_settings['totals']['color'])

    fig_rgi = figures.rgi_breakdown_figure(data, type_value=fig_settings['rgi']['type'])

    return {
        'map': fig_map,
        'timeline': fig_histogram_rate,
        'totals': fig_totals,
        'rgi': fig_rgi,
    }
