from typing import List, Dict
import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas

from card_live_dashboard.model.CardLiveData import CardLiveData

logger = logging.getLogger(__name__)

# Creation of empty figure adapted from https://community.plotly.com/t/replacing-an-empty-graph-with-a-message/31497
EMPTY_FIGURE = go.Figure(layout={
    'xaxis': {'visible': False},
    'yaxis': {'visible': False},
    'annotations': [{
        'text': 'No matching data found',
        'xref': 'paper',
        'yref': 'paper',
        'showarrow': False,
        'font': {
            'size': 28
        }
    }]
})

# Create empty geographic map
EMPTY_MAP = go.Figure(go.Scattergeo())

# Empty figures to display initially
EMPTY_FIGURE_DICT = {
    'map': EMPTY_MAP,
    'timeline': EMPTY_FIGURE,
    'totals': EMPTY_FIGURE,
    'rgi': EMPTY_FIGURE,
}

TOTALS_COLUMN_SELECT_NAMES = {
    'default': 'geo_area_name_standard',
    'geographic': 'geo_area_name_standard',
    'organism_lmat': 'lmat_taxonomy',
    'organism_rgi_kmer': 'rgi_kmer_taxonomy'
}

TOTALS_COLUMN_DATAFRAME_NAMES = {
    'default': None,
    'geographic': 'geo_area_name_standard',
    'organism_lmat': 'lmat_taxonomy',
    'organism_rgi_kmer': 'rgi_kmer_taxonomy'
}

TOTALS_FIGURE_TITLES = {
    'geographic': 'Totals by geographic region',
    'organism_lmat': 'Totals by organism',
    'organism_rgi_kmer': 'Totals by organism'
}


RGI_TITLES = {
    'drug_class': 'Drug class resistances',
    'amr_gene': 'AMR gene',
    'amr_gene_family': 'AMR gene family',
    'resistance_mechanism': 'Resistance mechanism',
}


def totals_figure(data: CardLiveData, type_value: str, color_by_value: str) -> go.Figure:
    type_col = TOTALS_COLUMN_SELECT_NAMES[type_value]
    color_col = TOTALS_COLUMN_SELECT_NAMES[color_by_value]
    if type_col == color_col or color_by_value == 'default':
        count_by_columns = [type_col]
    else:
        count_by_columns = [type_col, color_col]

    if data.empty:
        fig = EMPTY_FIGURE
    else:
        totals_df = data.sample_counts(count_by_columns).reset_index()

        type_col_name = TOTALS_COLUMN_DATAFRAME_NAMES[type_value]
        color_col_name = TOTALS_COLUMN_DATAFRAME_NAMES[color_by_value]

        category_orders = order_categories(totals_df, type_col_name, by_sum=True, sum_col='count')
        if color_by_value != 'default':
            category_orders.update(
                order_categories(totals_df, color_col_name, by_sum=True, sum_col='count')
            )

        fig = px.bar(totals_df, y=type_col_name, x='count',
                     color=color_col_name,
                     height=600,
                     category_orders=category_orders,
                     labels={'count': 'Samples count',
                             'geo_area_name_standard': 'Geographic region',
                             'rgi_kmer_taxonomy': 'Organism (RGI Kmer)',
                             'lmat_taxonomy': 'Organism'},
                     title=TOTALS_FIGURE_TITLES[type_value],
                     )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': ''}
                          )

    return fig


def rgi_breakdown_figure(data: CardLiveData, type_value: str) -> go.Figure:
    if data.empty:
        fig = EMPTY_FIGURE
    else:
        totals_df = data.rgi_parser.explode_column('rgi_main.Drug Class')
        print(totals_df.columns)
        totals_df = data.rgi_parser.get_column_values(data_type=type_value)

        # Data preparation
        totals_df.name = 'categories'
        totals_df = totals_df.reset_index().drop_duplicates().set_index('filename')
        counts_df = totals_df.value_counts().to_frame().rename(columns={0: 'match_count'})
        selected_files_count = len(set(totals_df.index.tolist()))
        counts_df['match_proportion'] = counts_df / selected_files_count
        counts_df = counts_df.reset_index()
        counts_df = counts_df.sort_values(by=['match_count', 'categories'], ascending=[True, False])
        counts_df = counts_df.rename(columns={'match_proportion': 'Match percent'})

        if counts_df.empty:
            fig = EMPTY_FIGURE
        else:
            title = RGI_TITLES[type_value]

            fig = px.bar(counts_df, y='categories', x='Match percent',
                         height=600,
                         labels={'categories': 'Categories',
                                 'variable': 'Type',
                                 'match_count': 'Samples count'},
                         hover_data=['match_count'],
                         title=title,
                         )
            fig.update_layout(font={'size': 14},
                              yaxis={'title': ''},
                              xaxis={'title': 'Percent of samples', 'tickformat': '.0%'}
                              )
    return fig


def choropleth_drug(data: CardLiveData, world: geopandas.GeoDataFrame):
    df_geo = data.sample_counts(['geo_area_code', 'geo_area_name_standard']).reset_index()

    # Remove N/A from counts so it doesn't mess with colors of map
    df_geo = df_geo[~df_geo['geo_area_name_standard'].str.contains('N/A')]

    if df_geo.empty or df_geo['count'].sum() == 0:
        fig = EMPTY_MAP
    else:
        fig = px.choropleth(df_geo, geojson=world, locations='geo_area_code',
                            featureidkey='properties.un_m49_numeric',
                            color='count', color_continuous_scale='YlGnBu',
                            hover_data=['geo_area_name_standard'],

                            # Off-center to avoid a color fill issue with Antarctica
                            # where the oceans get filled instead of the continent
                            center={'lat': 0, 'lon': 0.01},

                            title='Samples by geographic region',
                            )

        fig.update_traces(
            hovertemplate=(
                '<b style="font-size: 125%;">%{customdata[0]}</b><br>'
                '<b>Count:</b>  %{z}<br>'
            )
        )

    fig.update_layout(
        margin={"r": 0, "t": 35, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='Count',
            yanchor='middle',
            y=0.5,
            len=1,
            lenmode='fraction',
            outlinecolor='black',
            outlinewidth=1,
            bgcolor='white',
            thickness=25,
            thicknessmode='pixels',
        ),
    )

    return fig


def build_time_histogram(data: CardLiveData, fig_type: str, color_by: str):
    if data.empty:
        fig = EMPTY_FIGURE
    else:
        if fig_type == 'cumulative_counts' or fig_type == 'counts':
            display_col = None
            yaxis_title = 'Samples count'
            tickformat = ''
            histfunc = 'count'

            hist_data = data.main_df

            if fig_type == 'counts':
                cumulative = False
            elif fig_type == 'cumulative_counts':
                cumulative = True
            else:
                raise Exception(f'Unknown value [fig_type={fig_type}]')
        elif fig_type == 'cumulative_percent' or fig_type == 'percent':
            display_col = 'time_fraction'
            yaxis_title = 'Percent of samples'
            tickformat = '.0%'
            histfunc = 'sum'

            # I add in a fraction of the total number of samples here
            # This is so I can make the histogram report a percentage
            # of values instead of a count (by taking the sum of
            # (time_fraction) in a given time period).
            hist_data = data.main_df.copy()
            hist_data[display_col] = 1 / len(hist_data)

            if fig_type == 'percent':
                cumulative = False
            elif fig_type == 'cumulative_percent':
                cumulative = True
            else:
                raise Exception(f'Unknown value [fig_type={fig_type}]')
        else:
            raise Exception(f'Unknown value [fig_type={fig_type}]')

        color_col_name = TOTALS_COLUMN_DATAFRAME_NAMES[color_by]

        if color_by == 'default':
            marginal = 'rug'
        else:
            # I get rid of marginal here since I found the plot became messy
            # when coloring by many categories
            marginal = None

        category_orders = order_categories(hist_data, color_col_name)

        fig = px.histogram(hist_data, x='timestamp', y=display_col,
                           nbins=50,
                           marginal=marginal,
                           cumulative=cumulative,
                           color=color_col_name,
                           category_orders=category_orders,
                           labels={'time_fraction': 'Percent of samples',
                                   'timestamp': 'Date',
                                   'geo_area_name_standard': 'Geographic region',
                                   'rgi_kmer_taxonomy': 'Organism (RGI Kmer)',
                                   'lmat_taxonomy': 'Organism'},
                           title='Samples by date',
                           histfunc=histfunc,
                           )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': yaxis_title, 'tickformat': tickformat}
                          )

        # This replaces the text in the hover 'sum of Percent of samples' to 'Percent of samples'
        for d in fig.data:
            d.hovertemplate = d.hovertemplate.replace('sum of ', '')
            d.hovertemplate = d.hovertemplate.replace('count', 'Samples count')

    return fig


def order_categories(df: pd.DataFrame, col: str, by_sum: bool = False, sum_col: str = None) -> Dict[str,List[str]]:
    """
    Reorders categories in the dataframe by the total counts in the passed column.
    :param df: The data frame.
    :param col: The column to order by. Pass None to return no order (empty dictionary).
    :return: A dictionary mapping the column to a list of indexes defining the order of categories in the data frame.
             Returns an empty dictionary if col is None.
             Returned as a dictionary to be directly passed to a plotly plot as the orders of categories.
    """
    if col is None:
        return {}
    else:
        if by_sum:
            ordered_list = df.groupby(col).sum().sort_values(by=[sum_col], ascending=False).index.tolist()
        else:
            ordered_list = df.groupby(col).size().sort_values(ascending=False).index.tolist()
        return {col: ordered_list}