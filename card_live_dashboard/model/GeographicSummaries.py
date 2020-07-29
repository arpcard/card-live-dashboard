import pandas as pd
import geopandas
import numpy as np
import json
from os import path
from pathlib import Path
from flatten_json import flatten

class GeographicSummaries:

    def __init__(self, region_codes):
        self._geographic_region_codes = region_codes

    def create_geo_analysis_table(self, main_df):
        df_geo = main_df[['geo_area_code', 'analysis_valid']].copy()

        df_geo = df_geo.groupby(
            ['geo_area_code', 'analysis_valid']).size().unstack().fillna(0).astype(int)

        # Create a 'Total' column
        df_totals = df_geo.sum(axis='columns').to_frame(name='Total')
        df_geo = df_geo.merge(df_totals, on='geo_area_code').reset_index()

        # Add region names
        df_geo = self._geographic_region_codes.add_region_standard_names(
            df_geo, 'geo_area_code').drop(columns=[self._geographic_region_codes.TOP_REGION_NAME])

        return df_geo

    def create_geo_timestamp_table(self, main_df):
        geo_time = main_df[['timestamp', 'geo_area_code']]
        geo_time = self._geographic_region_codes.add_region_standard_names(geo_time, 'geo_area_code')
        geo_time = geo_time.drop(columns=[self._geographic_region_codes.TOP_REGION_NAME])

        totals = geo_time.groupby(['geo_area_code']).size().rename('total_in_geo_area')
        geo_time = geo_time.merge(totals, on='geo_area_code', how='left')

        return geo_time