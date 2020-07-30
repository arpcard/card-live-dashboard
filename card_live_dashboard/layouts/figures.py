import pandas as pd
import plotly.express as px
import geopandas


def taxonomic_comparison(df: pd.DataFrame):
    df = df.sort_values(by='Total').reset_index()

    label = 'Other (count <= 3)'
    df.loc[df['Total'] <= 3, 'taxon'] = label
    df = df.groupby('taxon').sum().sort_values(
        by=['Total', 'taxon'], ascending=True)
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
        yaxis=dict(tickfont=dict(size=12), dtick=1),
        font={'size': 18}
    )

    return fig


def choropleth_drug(geo_drug_classes_count: pd.DataFrame, world: geopandas.GeoDataFrame):
    fig = px.choropleth(geo_drug_classes_count, geojson=world, locations='geo_area_code',
                        featureidkey='properties.un_m49_numeric',
                        color='drug_class_count', color_continuous_scale='YlGnBu',
                        labels={'drug_class_count': 'Count'},
                        hover_data=['geo_area_name_standard'],
                        center={'lat': 0, 'lon': 0.01},
                        )
    fig.update_geos()
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


def build_time_histogram(df_drug_mapping: pd.DataFrame, cumulative: bool):
    fig = px.histogram(df_drug_mapping, x='timestamp',
                       nbins=50,
                       labels={'count': 'Count',
                               'timestamp': 'Date'},
                       title='Histogram of samples over time',
                       )
    fig.update_traces(cumulative_enabled=cumulative)
    fig.update_layout(font={'size': 16},
                      height=350)

    return fig
