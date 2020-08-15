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
    'resistances': EMPTY_FIGURE,
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
    'organism_lmat': 'Totals by organism (LMAT)',
    'organism_rgi_kmer': 'Totals by organism (RGI Kmer)'
}


RESISTANCES_TITLES = {
    'drug_class': 'Drug class resistances',
    'amr_gene': 'AMR gene',
}


def taxonomic_comparison(df: pd.DataFrame):
    if df.empty:
        fig = EMPTY_FIGURE
    else:
        CATEGORY_LIMIT = 10
        df = df.groupby('taxon').sum().sort_values(
            by=['Total', 'taxon'], ascending=True)

        if len(df) > CATEGORY_LIMIT:
            df = df.reset_index()
            label = 'Other'
            df['selected'] = False
            # CATEGORY_LIMIT - 1 so that the 'Other' label becomes the final category
            df.loc[df.tail(CATEGORY_LIMIT - 1).index.tolist(), 'selected'] = True
            df.loc[~df['selected'], 'taxon'] = label
            df = df.drop(columns=['selected'])
            df = df.groupby('taxon').sum().sort_values(
                by=['Total', 'taxon'], ascending=True)

            # Shift 'Other' label to bottom
            df_old_index = df.index.tolist()
            df_old_index.pop(df.index.get_loc(label))
            df_new_index = [label] + df_old_index
            df = df.reindex(df_new_index)

        df = df.rename(columns={'count_both': 'Both LMAT and RGI Kmer',
                                'rgi_counts': 'Unique to RGI Kmer',
                                'lmat_counts': 'Unique to LMAT'})

        stacked_columns = [e for e in list(df.columns) if e not in ('Total')]

        fig = px.bar(df, y=df.index, x=stacked_columns, height=700,
                     labels={'value': 'Number of genomes',
                             'variable': 'Taxonomic software agreement',
                             'taxon': 'Taxononmic category'},
                     title='Breakdown of genome to taxonomic category assignments')
        fig.update_layout(
            yaxis=dict(tickfont=dict(size=14), dtick=1),
            font={'size': 14}
        )

    return fig


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
        totals_df = data.value_counts(count_by_columns).reset_index()

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
                             'lmat_taxonomy': 'Organism (LMAT)'},
                     title=TOTALS_FIGURE_TITLES[type_value],
                     )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': '', 'dtick': 1}
                          )

    return fig


def resistance_breakdown_figure(data: CardLiveData, type_value: str) -> go.Figure:
    if data.empty:
        fig = EMPTY_FIGURE
    else:
        if type_value == 'drug_class':
            totals_df = data.rgi_parser.explode_column('rgi_main.Drug Class')['rgi_main.Drug Class_exploded']
        elif type_value == 'amr_gene':
            totals_df = data.rgi_df['rgi_main.Best_Hit_ARO']
        else:
            raise Exception(f'Unknown value [type_value={type_value}]')

        # Data preparation
        totals_df.name = 'categories'
        totals_df = totals_df.reset_index().drop_duplicates().set_index('filename')
        counts_df = totals_df.value_counts().to_frame().rename(columns={0: 'match_count'})
        selected_files_count = len(set(totals_df.index.tolist()))
        counts_df['match_proportion'] = counts_df / selected_files_count
        counts_df = counts_df.reset_index()
        counts_df = counts_df.sort_values(by=['match_count', 'categories'], ascending=[True, False])
        counts_df = counts_df.rename(columns={'match_proportion': 'Match percent'})

        title = RESISTANCES_TITLES[type_value]

        fig = px.bar(counts_df, y='categories', x='Match percent',
                     height=600,
                     labels={'categories': 'Categories',
                             'variable': 'Type',
                             'match_count': 'Samples count'},
                     hover_data=['match_count'],
                     title=title,
                     )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': '', 'dtick': 1},
                          xaxis={'title': 'Percent of samples', 'tickformat': '.0%'}
                          )
    return fig


def choropleth_drug(data: CardLiveData, world: geopandas.GeoDataFrame):
    df_geo = data.value_counts(['geo_area_code', 'geo_area_name_standard']).reset_index()

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
        if fig_type == 'cumulative':
            cumulative = True
        elif fig_type == 'rate':
            cumulative = False
        else:
            raise Exception(f'Unknown value [fig_type={fig_type}]')

        color_col_name = TOTALS_COLUMN_DATAFRAME_NAMES[color_by]

        if color_by == 'default':
            marginal = 'rug'
        else:
            # I get rid of marginal here since I found the plot became messy
            # when coloring by many categories
            marginal = None

        # I add in a fraction of the total number of samples here
        # This is so I can make the histogram report a percentage
        # of values instead of a count (by taking the sum of
        # (time_fraction) in a given time period).
        hist_data = data.main_df.copy()
        hist_data['time_fraction'] = 1/len(hist_data)

        category_orders = order_categories(hist_data, color_col_name)

        fig = px.histogram(hist_data, x='timestamp', y='time_fraction',
                           nbins=50,
                           marginal=marginal,
                           cumulative=cumulative,
                           color=color_col_name,
                           category_orders=category_orders,
                           labels={'time_fraction': 'Percent of samples',
                                   'timestamp': 'Date',
                                   'geo_area_name_standard': 'Geographic region',
                                   'rgi_kmer_taxonomy': 'Organism (RGI Kmer)',
                                   'lmat_taxonomy': 'Organism (LMAT)'},
                           title='Samples by date',
                           histfunc='sum',
                           )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': 'Percent of samples', 'tickformat': '.0%'}
                          )

        # This replaces the text in the hover 'sum of Percent of samples' to 'Percent of samples'
        for d in fig.data:
            d.hovertemplate = d.hovertemplate.replace('sum of ', '')

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