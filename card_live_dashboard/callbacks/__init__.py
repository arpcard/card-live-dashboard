from typing import List, Set, Dict
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import dash

from card_live_dashboard.service.CardLiveDataManager import CardLiveDataManager
from card_live_dashboard.model.CardLiveData import CardLiveData
import card_live_dashboard.layouts.figures as figures
from card_live_dashboard.model import world

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
        Output('organism-parameters', 'is_open'),
        [Input('organism-parameters-toggle', 'n_clicks')],
        [State('organism-parameters', 'is_open')],
    )
    def toggle_organism_parameters_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        [Output('global-sample-count', 'children'),
         Output('global-most-recent', 'children'),
         Output('time-period-items', 'options'),
         Output('organism-lmat-select', 'options'),
         Output('organism-rgi-kmer-select', 'options'),
         Output('selected-samples-count', 'children'),
         Output('drug-class-select', 'options'),
         Output('amr-gene-select', 'options'),
         Output('figure-geographic-map-id', 'figure'),
         Output('figure-timeline-id', 'figure'),
         Output('figure-totals-id', 'figure'),
         Output('figure-resistances-id', 'figure')],
        [Input('rgi-cutoff-select', 'value'),
         Input('drug-class-select', 'value'),
         Input('amr-gene-select', 'value'),
         Input('organism-lmat-select', 'value'),
         Input('organism-rgi-kmer-select', 'value'),
         Input('time-period-items', 'value'),
         Input('timeline-type-select', 'value'),
         Input('timeline-color-select', 'value'),
         Input('totals-type-select', 'value'),
         Input('totals-color-select', 'value'),
         Input('resistances-type-select', 'value'),
         Input('auto-update-interval', 'n_intervals')]
    )
    def update_all_figures(rgi_cutoff_select: str, drug_classes: List[str],
                           amr_genes: List[str], organism_lmat: str,
                           organism_rgi_kmer: str, time_dropdown: str,
                           timeline_type_select: str, timeline_color_select: str,
                           totals_type_select: str, totals_color_select: str,
                           resistances_type_select: str, n_intervals):
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

        time_subsets = apply_filters(data=data,
                                     rgi_cutoff_select=rgi_cutoff_select,
                                     drug_classes=drug_classes,
                                     amr_genes=amr_genes,
                                     organism_lmat=organism_lmat,
                                     organism_rgi_kmer=organism_rgi_kmer)

        fig_settings = {
            'timeline': {'type': timeline_type_select, 'color': timeline_color_select},
            'totals': {'type': totals_type_select, 'color': totals_color_select},
            'resistances': {'type': resistances_type_select}
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

        organism_lmat_options = build_options([organism_lmat], time_subsets[time_dropdown].unique_column('lmat_taxonomy'))
        organism_rgi_kmer_options = build_options([organism_rgi_kmer], time_subsets[time_dropdown].unique_column('rgi_kmer_taxonomy'))
        drug_class_options = build_options(drug_classes, time_subsets[time_dropdown].rgi_parser.all_drugs())
        amr_gene_options = build_options(amr_genes, time_subsets[time_dropdown].rgi_parser.all_amr_genes())

        return (global_samples_count,
                global_last_updated,
                time_dropdown_text,
                organism_lmat_options,
                organism_rgi_kmer_options,
                samples_count_string,
                drug_class_options,
                amr_gene_options,
                main_pane_figures['map'],
                main_pane_figures['timeline'],
                main_pane_figures['totals'],
                main_pane_figures['resistances'])


def apply_filters(data: CardLiveData, rgi_cutoff_select: str,
                  drug_classes: List[str], amr_genes: List[str], organism_lmat: str,
                  organism_rgi_kmer: str) -> Dict[str, CardLiveData]:
    time_now = datetime.now()

    data = data.select(table='rgi', by='cutoff', type='row', level=rgi_cutoff_select) \
        .select(table='rgi', by='drug', type='file', drug_classes=drug_classes) \
        .select(table='rgi', by='amr_gene', type='file', amr_genes=amr_genes) \
        .select(table='main', by='lmat_taxonomy', taxonomy=organism_lmat) \
        .select(table='main', by='rgi_kmer_taxonomy', taxonomy=organism_rgi_kmer)

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


def build_main_pane(data: CardLiveData, fig_settings: Dict[str, Dict[str, str]]):
    fig_map = figures.choropleth_drug(data, world)
    fig_histogram_rate = figures.build_time_histogram(data, fig_type=fig_settings['timeline']['type'],
                                                      color_by=fig_settings['timeline']['color'])
    fig_totals = figures.totals_figure(data, type_value=fig_settings['totals']['type'],
                                       color_by_value=fig_settings['totals']['color'])

    fig_drug_classes = figures.resistance_breakdown_figure(data, type_value=fig_settings['resistances']['type'])

    return {
        'map': fig_map,
        'timeline': fig_histogram_rate,
        'totals': fig_totals,
        'resistances': fig_drug_classes,
    }
