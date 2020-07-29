from types import FunctionType
from pathlib import Path
import pandas as pd
import geopandas


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

    def insert_geo_name_na_mapping(self, function: FunctionType):
        '''
        Inserts a new mapping function letting you customize how m49 codes get mapped to geographic area names for N/A values.
        Used for custom mappings not part of the UN M49 standard (e.g., 0 to 'Mulitiple regions'). Use this like

        GeographicRegionCodes g = GeographicRegionCodes('file.csv')
        g.insert_geo_name_na_mapping(lambda x: 'Multiple regions' if x == '0' else None)

        :param function: The function to use for mapping.

        :return: None
        '''
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

        return self.dissolve_un_m49_regions(world)
