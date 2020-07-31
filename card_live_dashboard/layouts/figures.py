import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas

# Creation of empty figure adapted from https://community.plotly.com/t/replacing-an-empty-graph-with-a-message/31497
empty_figure = go.Figure(layout={
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


def taxonomic_comparison(df: pd.DataFrame):
    if df.empty:
        fig = empty_figure
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


def geographic_totals(df):
    if df.empty:
        fig = go.Figure(go.Scattergeo())
    else:
        df = df.sort_values(by=['count'], ascending=True)
        fig = px.bar(df, y='geo_area_name_standard', x='count',
                     labels={'count': 'Count'},
                     title='Samples by region',
        )
        fig.update_layout(font={'size': 14},
                          yaxis={'title': '', 'dtick': 1}
        )

    return fig

def choropleth_drug(geo_drug_classes_count: pd.DataFrame, world: geopandas.GeoDataFrame):
    if geo_drug_classes_count.empty or geo_drug_classes_count['count'].sum() == 0:
        fig = go.Figure(go.Scattergeo())
    else:
        fig = px.choropleth(geo_drug_classes_count, geojson=world, locations='geo_area_code',
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


def build_time_histogram(df_time: pd.DataFrame, cumulative: bool):
    if df_time.empty:
        fig = empty_figure
    else:
        fig = px.histogram(df_time, x='timestamp',
                           nbins=50,
                           labels={'count': 'Count',
                                   'timestamp': 'Date'},
                           title='Samples by date',
        )
        fig.update_traces(cumulative_enabled=cumulative)
        fig.update_layout(font={'size': 14},
                          yaxis={'title': 'Count'}
        )
    return fig