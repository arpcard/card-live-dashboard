import logging
from collections import OrderedDict
from typing import List, Dict

import geopandas
import upsetplot
import pandas as pd
import plotly.express as px
import plotly.subplots as sbp
import plotly.graph_objects as go

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
    'intersections': EMPTY_FIGURE,
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

RGI_D_TICK = {
    'drug_class': 1,
    'amr_gene': None,
    'amr_gene_family': None,
    'resistance_mechanism': 1,
}

# Spacing to put between tick mark labels and plot
TICKSPACE = ' '


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
                     height=get_figure_height(len(totals_df[type_col_name].unique())),
                     category_orders=category_orders,
                     labels={'count': 'Samples count',
                             'geo_area_name_standard': 'Geographic region',
                             'lmat_taxonomy': 'Organism',
                             'rgi_kmer_taxonomy': 'Organism'},
                     title=TOTALS_FIGURE_TITLES[type_value],
                     )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': '', 'ticksuffix': TICKSPACE}
                          )

    return fig


def rgi_intersection_figure(data: CardLiveData, type_value: str) -> go.Figure:
    if data.empty:
        fig = EMPTY_FIGURE
    else:
        title = RGI_TITLES[type_value]
        totals_df = data.rgi_parser.get_column_values(data_type=type_value, values_name='categories', drop_duplicates=True)
        totals_df = totals_df.dropna()
        category_sets = totals_df.reset_index().groupby('filename').agg(lambda x: tuple(x)).applymap(list)
        category_sets = category_sets['categories'].apply(lambda x: sorted(x)).sort_values().apply(tuple)
        category_sets = category_sets.value_counts()

        total_categories = totals_df['categories'].nunique()

        # if the data is empty
        if category_sets.empty:
            fig = EMPTY_FIGURE
        # or if there is way too much data to plot
        elif totals_df['categories'].nunique() > 40:
            fig = go.Figure(layout={
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f"{total_categories} Total {title} types with current selection<br>Too much data to plot intersections, please subset further",
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {
                        'size': 28
                    }
                }]
            })
        else:
            upset_data = upsetplot.from_memberships(category_sets.index, category_sets.values)

			# filter to top 25 sets by cardinality
            if upset_data.shape[0] > 25:
                truncated = True
                upset_data = upset_data[:25]
            else:
                truncated = False

            upset_data = upsetplot.UpSet(upset_data, sort_by='cardinality')

            categories = ["<br>".join(sorted([cat for cat, presence in zip(upset_data.intersections.index.names, mask) if presence])) \
			                                  for mask in upset_data.intersections.index]

            set_intersections = upset_data.intersections.reset_index().drop(0, axis=1).astype(int).T.iloc[::-1]

            # make grid for set memberships
            grid_x = []
            grid_y = []
            membership_x = []
            membership_y = []
            names = []

            y = 0
            for row in set_intersections.iterrows():
                x = 0
                for membership in row[1]:
                    grid_x.append(x)
                    grid_y.append(y)
                    if membership == 1:
                        membership_x.append(x)
                        membership_y.append(y)
                        names.append(row[0])
                    x+=1
                y+=1

            # create subplot layout
            fig = sbp.make_subplots(rows=2, cols=2,
                                    column_widths=[2, 0.2],
                                    row_heights=[0.4, 2],
                                    horizontal_spacing = 0.005,
                                    vertical_spacing=0.01)

            # add barplot of intersection cardinalities
            fig.add_trace(go.Bar(y=upset_data.intersections.values,
                                 x=categories,
                                 name=f"{title} Set Cardinality",
                                 showlegend=False,
                                 hovertemplate='Genomes w/ Set: %{y}<br>Set: [%{x}]',
                                 xaxis='x1',
                                 yaxis='y1'),
                          row=1, col=1),

            # add barplot of count of category values
            fig.add_trace(go.Bar(y = upset_data.totals.iloc[::-1].index,
                                 x=upset_data.totals.iloc[::-1],
                                 orientation='h',
                                 name=f"{title} Unique Counts",
                                 showlegend=False,
                                 hovertemplate='Category: %{y}<br>Genomes: %{x}',
                                 yaxis='y2',
                                 xaxis='x2'),
                          row=2, col=2)

            # create the backgrid for the set memberships
            fig.add_trace(go.Scatter(x = grid_x,
                                     y = grid_y,
                                     hoverinfo='skip',
                                     mode='markers',
                                     marker={'color': 'lightgrey'},
                                     showlegend=False,
                                     xaxis='x3',
                                     yaxis='y3'),
                          row=2, col=1)

            # plot the set memberships
            fig.add_trace(go.Scatter(x = membership_x,
                                     y = membership_y,
                                     name=f"{title} Set Intersections",
                                     hovertext=names,
                                     hovertemplate='%{hovertext}',
                                     mode='markers',
                                     marker={'color': 'blue'},
                                     xaxis='x4',
                                     yaxis='y4',
                                     showlegend=False),
                            row=2, col=1)

            # tidy up layout, disable and align axes so everything joins
            # there may be a better way to do this with shared/aligned axes
            # across plots that still allows zooming but I can't figure it out
            # right now!
            if truncated:
                plot_label = f"{title} UpSet Plot<br>(Truncated to 25 Most Common Intersections)"
            else:
                plot_label = f"{title} UpSet Plot<br>(All Intersections)"

            fig.update_layout(dict(
                title = plot_label,
                # cardinality
                xaxis1 = dict(showticklabels=False,
                              fixedrange=True),
                yaxis1 = dict(title="Cardinality",
                              fixedrange=True),

                # grid
                xaxis2 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.columns)-0.5]),
                yaxis2 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.index)+0.5]),

                # membership
                xaxis3 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.columns)-0.5]),
                yaxis3 = dict(
                    tickmode = 'array',
                    tickvals = list(range(len(set_intersections.index))),
                    ticktext = set_intersections.index,
                    title=f"{title}",
                    fixedrange=True,
                    range=[-0.5, len(set_intersections.index)+0.5],
                    tickfont=dict(size = 10),
                    automargin=True,
                ),

                # category count
                xaxis4 = dict(title="Unique Count",
                              fixedrange=True),
                yaxis4 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[0, len(set_intersections.index)+0.5])
            )
            )
            fig.update_layout(height=get_figure_height(total_categories))

    return fig


def rgi_breakdown_figure(data: CardLiveData, type_value: str, color_by_value: str) -> go.Figure:
    if data.empty:
        fig = EMPTY_FIGURE
    else:
        color_by_col = TOTALS_COLUMN_DATAFRAME_NAMES[color_by_value]
        category_order = {}

        totals_df = data.rgi_parser.get_column_values(
            data_type=type_value, values_name='categories', drop_duplicates=True)

        # Data preparation
        selected_files_count = len(set(totals_df.index.tolist()))
        categories_total = totals_df['categories'].value_counts().to_frame('categories_total')

        if color_by_col is not None:
            hover_data = ['count', 'categories_total', 'categories_total_percent']

            color_by_df = data.main_df[color_by_col]
            totals_df = totals_df.merge(color_by_df, how='left', left_index=True, right_index=True).reset_index()
            counts_df = totals_df.groupby(['categories', color_by_col]).size().to_frame()
            counts_df = counts_df.rename(columns={0: 'count'}).reset_index()

            # Define the order of the color_by column so that the category with the highest count gets displayed first
            color_counts_df = counts_df[[color_by_col, 'count']].groupby(
                color_by_col).agg('sum').sort_values(by='count', ascending=False)
            category_order[color_by_col] = color_counts_df.index.tolist()
        else:
            hover_data = ['count']

            counts_df = totals_df.groupby('categories').size().to_frame()
            counts_df = counts_df.rename(columns={0: 'count'}).reset_index()

        counts_df = counts_df.merge(categories_total, how='left', left_on='categories', right_index=True)
        counts_df['proportion'] = counts_df['count'] / selected_files_count

        # I convert to percent (instead of proportion) here since plotly is not doing the auto-conversion of
        # proportion to percents (unlike for 'proportion' which is the column displayed so plotly does auto-conversion)
        counts_df['categories_total_percent'] = 100 * (counts_df['categories_total'] / selected_files_count)
        counts_df['categories_total_percent'] = counts_df['categories_total_percent'].apply(lambda x: f'{x:,.0f}%')

        # Define order to display
        display_category_order = counts_df[['categories', 'categories_total']].sort_values(
            by='categories_total', ascending=False)['categories'].tolist()
        # Create a list of unique categories while still preserving order of the original list
        display_category_order = list(OrderedDict.fromkeys(display_category_order))
        category_order['categories'] = display_category_order

        if counts_df.empty:
            fig = EMPTY_FIGURE
        else:
            title = RGI_TITLES[type_value]
            rgi_d_tick = RGI_D_TICK[type_value]

            fig = px.bar(counts_df, y='categories', x='proportion',
                         category_orders=category_order,
                         height=get_figure_height(len(counts_df['categories'].unique())),
                         color=color_by_col,
                         labels={
                             'categories': 'Categories',
                             'variable': 'Type',
                             'count': 'Samples count',
                             'categories_total': 'Total samples in category count',
                             'categories_total_percent': 'Total samples in category percent',
                             'proportion': 'Percent of samples',
                             'geo_area_name_standard': 'Geographic region',
                             'lmat_taxonomy': 'Organism',
                             'rgi_kmer_taxonomy': 'Organism',
                             'match_count': 'Samples count'
                         },
                         hover_data=hover_data,
                         title=title,
                         )
            fig.update_layout(font={'size': 14},
                              yaxis={'title': '', 'dtick': rgi_d_tick, 'ticksuffix': TICKSPACE, 'automargin': True},
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
                                   'rgi_kmer_taxonomy': 'Organism',
                                   'lmat_taxonomy': 'Organism'},
                           title='Samples by date',
                           histfunc=histfunc,
                           )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': yaxis_title, 'tickformat': tickformat, 'ticksuffix': TICKSPACE}
                          )

        # This replaces the text in the hover 'sum of Percent of samples' to 'Percent of samples'
        for d in fig.data:
            d.hovertemplate = d.hovertemplate.replace('sum of ', '')
            d.hovertemplate = d.hovertemplate.replace('count', 'Samples count')

    return fig


def order_categories(df: pd.DataFrame, col: str, by_sum: bool = False, sum_col: str = None) -> Dict[str, List[str]]:
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


def get_figure_height(number_categories: int) -> int:
    """
    Given a number of categories to plot gets an appropriate figure height.
    :param number_categories: The number of categories to plot.
    :return: A figure height to be used by plotly.
    """
    if number_categories < 10:
        return 400
    elif number_categories < 20:
        return 500
    elif number_categories < 30:
        return 600
    else:
        return 800
