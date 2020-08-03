from typing import Dict, Union, Callable
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas
import shapely.geometry.multipolygon as multipolygon
import logging

logger = logging.getLogger(__name__)


class GeographicRegionCodes:
    TOP_REGION_NAME = 'geo_area_toplevel_m49code'
    SUB_REGION_CODE = 'geo_area_sublevel_m49code'
    COUNTRY_CODE = 'geo_area_iso3_code'
    NAME_COL = 'geo_area_name_standard'

    def __init__(self, unm49_filepath: Path, use_default_additional_mappings: bool = True):
        self._unm49_data = pd.read_csv(unm49_filepath, dtype=str)
        self._unm49_mapping = self._load_unm49_region_mapping_table(self._unm49_data)

        self._mapping_functions = []

        if use_default_additional_mappings:
            self.insert_geo_name_na_mapping(lambda x: 'Multiple regions' if int(x) == 0 else None)
            self.insert_geo_name_na_mapping(lambda x: f'N/A [code={x}]')

    def insert_geo_name_na_mapping(self, function: Callable):
        """
        Inserts a new mapping function letting you customize how m49 codes get mapped to geographic area names for N/A values.
        Used for custom mappings not part of the UN M49 standard (e.g., 0 to 'Mulitiple regions'). Use this like

        GeographicRegionCodes g = GeographicRegionCodes('file.csv')
        g.insert_geo_name_na_mapping(lambda x: 'Multiple regions' if x == '0' else None)

        :param function: The function to use for mapping.

        :return: None
        """
        self._mapping_functions.append(function)

    def _load_unm49_region_mapping_table(self, df: pd.DataFrame) -> pd.DataFrame:
        df_global = df[['Global Code', 'Global Name', 'M49 Code', 'ISO-alpha3 Code']].rename(
            columns={'Global Code': self.TOP_REGION_NAME,
                     'Global Name': self.NAME_COL,
                     'ISO-alpha3 Code': self.COUNTRY_CODE,
                     'M49 Code': self.SUB_REGION_CODE})
        df_region = df[['Region Code', 'Region Name', 'M49 Code', 'ISO-alpha3 Code']].rename(
            columns={'Region Code': self.TOP_REGION_NAME,
                     'Region Name': self.NAME_COL,
                     'ISO-alpha3 Code': self.COUNTRY_CODE,
                     'M49 Code': self.SUB_REGION_CODE})
        df_sub_region = df[['Sub-region Code', 'Sub-region Name', 'M49 Code', 'ISO-alpha3 Code']].rename(
            columns={'Sub-region Code': self.TOP_REGION_NAME,
                     'Sub-region Name': self.NAME_COL,
                     'ISO-alpha3 Code': self.COUNTRY_CODE,
                     'M49 Code': self.SUB_REGION_CODE})
        df_intermediate_region = df[
            ['Intermediate Region Code', 'Intermediate Region Name', 'M49 Code', 'ISO-alpha3 Code']].rename(
            columns={'Intermediate Region Code': self.TOP_REGION_NAME,
                     'Intermediate Region Name': self.NAME_COL,
                     'ISO-alpha3 Code': self.COUNTRY_CODE,
                     'M49 Code': self.SUB_REGION_CODE})
        df_m49 = df[['M49 Code', 'Country or Area', 'M49 Code', 'ISO-alpha3 Code']]
        df_m49.columns = [self.TOP_REGION_NAME, self.NAME_COL, self.SUB_REGION_CODE, self.COUNTRY_CODE]

        return pd.concat([df_global, df_region, df_sub_region, df_intermediate_region, df_m49]).drop_duplicates(
            keep='first')

    def _apply_mapping_functions(self, data: pd.DataFrame, region_column: str):
        for mapping_function in self._mapping_functions:
            data.loc[data[self.NAME_COL].isna(),
                     self.NAME_COL] = data.loc[data[self.NAME_COL].isna(),
                                               region_column].apply(mapping_function)

        return data

    def add_region_standard_names(self, data: pd.DataFrame, region_column: str) -> pd.DataFrame:
        data = data.astype({region_column: str})
        region_standard_names = self._unm49_mapping[[self.TOP_REGION_NAME, self.NAME_COL]].drop_duplicates(
            keep='first').dropna()
        data_expanded = data.merge(region_standard_names, how='left', left_on=region_column,
                                   right_on=self.TOP_REGION_NAME)

        data_expanded = self._apply_mapping_functions(data_expanded, region_column)

        return data_expanded

    def expand_to_country_codes(self, data: pd.DataFrame, region_column: str) -> pd.DataFrame:
        data = data.astype({region_column: str})
        regions_no_names = self._unm49_mapping.drop(columns=[self.NAME_COL])
        data_expanded = data.merge(regions_no_names, how='left', left_on=region_column, right_on=self.TOP_REGION_NAME)

        return data_expanded

    def dissolve_un_m49_regions(self, world: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
        codes_mapping = self._unm49_data[['Region Code', 'Region Name', 'Sub-region Code', 'Sub-region Name',
                                          'Intermediate Region Code', 'Intermediate Region Name', 'ISO-alpha3 Code',
                                          'Country or Area', 'M49 Code']]
        world = world.merge(codes_mapping, left_on='iso_a3', right_on='ISO-alpha3 Code', how='left')

        world_regions = []

        for level in ['Region', 'Sub-region', 'Intermediate Region']:
            code_label = f'{level} Code'
            name_label = f'{level} Name'

            regions_group = world.dissolve(by=code_label)[['geometry', name_label]].rename(columns={name_label: 'name'})
            regions_group.index.name = 'id'
            regions_group.index = regions_group.index.astype('int64')

            world_regions.append(regions_group)

        antartica = world[world['ISO-alpha3 Code'] == 'ATA'][['geometry', 'M49 Code', 'Country or Area']]
        antartica = antartica.rename(columns={'M49 Code': 'id', 'Country or Area': 'name'}).astype(
            {'id': 'int64'}).set_index('id')
        world_regions.append(antartica)

        world = pd.concat(world_regions)
        world['un_m49_numeric'] = world.index.astype('int64')
        world.index = world.index.astype('str')

        return world

    def get_un_m49_regions_naturalearth(self) -> geopandas.GeoDataFrame:
        world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

        # Fix ISO-alpha3 codes which are not set.
        # See <https://github.com/geopandas/geopandas/issues/1041>.
        # ISO-alpha3 codes taken from UN website <https://unstats.un.org/unsd/methodology/m49/>.
        # Some of these were unset because they are disputed territories. Since I am only displaying
        #  course-grained geographic regions I am setting all these so they merge into the larger region properly.
        world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
        world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
        world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
        world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'

        world = self.split_france_french_guiana(world)

        return self.dissolve_un_m49_regions(world)

    def split_france_french_guiana(self, world: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
        """
        Splits up France into two regions: (1) main France and (2) French Guiana.
         This is done because the Natural Earth map combines both these regions together (so French Guiana
         is a part of Europe). But, the UN standard region codes groups French Guiana as part of South America.

        :param world: The GeoDataFrame representing the world.
        :return: A new GeoDataFrame with France and French Guiana split (or the original data frame if some error occured).
        """
        world_new = world

        if len(world[world['iso_a3'] == 'GUF']) != 0:
            logger.info('French Guiana [GUF] already exists in world map. Will not attempt to split France region.')
        else:
            shapes_france = world[world['iso_a3'] == 'FRA']['geometry'].values[0]
            split_regions = self.split_geoms_france(shapes_france)
            if split_regions is not None:
                world_new = world.copy()

                # Update France geometry
                original_france_entry = world_new.loc[world_new['iso_a3'] == 'FRA', 'geometry']
                new_france_entry = geopandas.GeoSeries(split_regions['FRA'], index=original_france_entry.index)
                world_new.loc[world_new['iso_a3'] == 'FRA', 'geometry'] = new_france_entry

                # Add French Guiana geometry
                french_guiana_row = world_new.loc[world_new['iso_a3'] == 'FRA'].reset_index().drop(columns=['index'])
                french_guiana_row['iso_a3'] = 'GUF'
                french_guiana_row['name'] = 'French Guiana'
                french_guiana_row['continent'] = 'South America'
                french_guiana_row['geometry'] = split_regions['GUF']
                world_new = world_new.append(french_guiana_row)
        return world_new

    def split_geoms_france(self, france_shape: multipolygon.MultiPolygon
                           ) -> Union[Dict[str, multipolygon.MultiPolygon], None]:
        """
        Splits up geometries of France into the main country and French Guiana.
        Used for merging French Guiana into the South American continent.

        :param france_shape: The Shapely shape of France.
        :return: A dictionary of the split shapes, like {'FRA': shape, 'GUI': shape}
                  or None to ignore spliting country.
        """

        # Area of French Guiana used to pull out Polygon from list of shapes
        # Area is based on units from coordinates of underlying object (lat/long), not distance units.
        GUF_AREA = 6.94

        split_regions = {'FRA': []}
        geoms = france_shape.geoms
        for g in geoms:
            if np.isclose(g.area, GUF_AREA, atol=1e-02):
                if not 'GUF' in split_regions:
                    split_regions['GUF'] = g
                else:
                    raise Exception('Already found French Guiana region')
            else:
                split_regions['FRA'].append(g)

        # Merge separate Polygon objects to single MultiPolygon
        if 'GUF' not in split_regions:
            logger.warning(('Could not find correct region for French Guiana [GUF] in French shape in map. '
                            f'Map areas: {[g.area for g in geoms]}. '
                            f'GUF assumed to have area [{GUF_AREA}]. '
                            'Will ignore trying to split region and leave map as default.')
                           )
            return None
        else:
            split_regions['FRA'] = multipolygon.MultiPolygon(split_regions['FRA'])
            return split_regions
