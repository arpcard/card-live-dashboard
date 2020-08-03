import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas

import card_live_dashboard.model as model
from card_live_dashboard.model.CardLiveData import CardLiveData

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
}

TOTALS_COLUMN_SELECT_NAMES = {
    'default': 'geo_area_code',
    'geographic': 'geo_area_code',
}

TOTALS_COLUMN_DATAFRAME_NAMES = {
    'default': None,
    'geographic': 'geo_area_name_standard',
}

TOTALS_FIGURE_TITLES = {
    'geographic': 'Geographic region'
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


def geographic_totals(data: CardLiveData, type_value: str, color_by_value: str) -> go.Figure:
    type_col = TOTALS_COLUMN_SELECT_NAMES[type_value]
    color_col = TOTALS_COLUMN_SELECT_NAMES[color_by_value]
    if type_col == color_col:
        count_by_columns = [type_col]
    else:
        count_by_columns = [type_col, color_col]

    totals_df = data.value_counts(count_by_columns).reset_index()

    if type_value == 'geographic':
        totals_df = model.region_codes.add_region_standard_names(totals_df, region_column='geo_area_code')

    print(totals_df)
    print(color_by_value)

    if totals_df.empty:
        fig = EMPTY_FIGURE
    else:
        totals_df = totals_df.sort_values(by=['count'], ascending=True)
        fig = px.bar(totals_df, y=TOTALS_COLUMN_DATAFRAME_NAMES[type_value], x='count',
                     color=TOTALS_COLUMN_DATAFRAME_NAMES[color_by_value],
                     labels={'count': 'Count'},
                     title=TOTALS_FIGURE_TITLES[type_value],
                     # hover_data=['geo_area_name_standard'],
                     )
        # fig.update_traces(
        #     hovertemplate=(
        #         '<b style="font-size: 125%;">%{customdata[0]}</b><br>'
        #         '<b>Count:</b>  %{x}<br>'
        #     )
        # )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': '', 'dtick': 1}
                          )

    return fig


def choropleth_drug(df_geo: pd.DataFrame, world: geopandas.GeoDataFrame):
    if df_geo.empty or df_geo['count'].sum() == 0:
        fig = EMPTY_MAP
    else:
        fig = px.choropleth(df_geo, geojson=world, locations='geo_area_code',
                            featureidkey='properties.un_m49_numeric',
                            color='count', color_continuous_scale='YlGnBu',
                            labels={'count': 'Count'},
                            hover_data=['geo_area_name_standard'],
                            center={'lat': 0, 'lon': 0.01},
                            )
        fig.update_traces(
            hovertemplate=(
                '<b style="font-size: 125%;">%{customdata[0]}</b><br>'
                '<b>Count:</b>  %{z}<br>'
            )
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=400,
    )

    return fig


def build_time_histogram(df_time: pd.DataFrame, fig_type: str, color_by: str):
    if df_time.empty:
        fig = EMPTY_FIGURE
    else:
        if fig_type == 'cumulative':
            cumulative = True
        elif fig_type == 'rate':
            cumulative = False
        else:
            raise Exception(f'Unknown value [fig_type={fig_type}]')

        if color_by == 'default':
            color = None
        elif color_by == 'geographic':
            color = 'geo_area_name_standard'
        elif color_by == 'organism_lmat':
            color = 'lmat.taxonomy_label'
        elif color_by == 'organism_rgi_kmer':
            color = 'rgi_kmer.taxonomy_label'
        else:
            raise Exception(f'Unknown value [color_by={color_by}]')

        fig = px.histogram(df_time, x='timestamp',
                           nbins=50,
                           color=color,
                           labels={'count': 'Count',
                                   'timestamp': 'Date',
                                   'geo_area_name_standard': 'Geographic region',
                                   'rgi_kmer.taxonomy_label': 'Organism (RGI Kmer)',
                                   'lmat.taxonomy_label': 'Organism (LMAT)'},
                           title='Samples by date',
                           )
        fig.update_traces(cumulative_enabled=cumulative)
        fig.update_layout(font={'size': 14},
                          yaxis={'title': 'Count'}
                          )
    return fig
