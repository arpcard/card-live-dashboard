from typing import List
from types import FunctionType

import pandas as pd
import numpy as np


class RGIParser:

    def __init__(self, df_rgi: pd.DataFrame):
        self._df_rgi = df_rgi
        self._drug_mapping = None

    def filter_by(self, func: FunctionType):
        """
        Applies a filter to the underlying dataframe to select specific columns.
        Can be run like:

        rgi_parser.filter_by(lambda x: x['column'] == 'value')

        :param func: The filter function.
        :return: A new instance of RGIParser which is a subset of the old instance.
        """
        return RGIParser(self._df_rgi[func(self._df_rgi)])

    def filter_by_cutoff(self, levels: List[str]):
        levels = [level.lower() for level in levels]
        return self.filter_by(lambda x: x['rgi_main.Cut_Off'].str.lower().isin(levels))

    def get_drug_mapping(self, drug_classes: List[str] = None) -> pd.DataFrame:
        df_rgi_drug = self._df_rgi.reset_index()[['filename', 'rgi_main.Drug Class']].replace('', np.nan)
        df_rgi_drug['rgi_main.Drug Class'] = df_rgi_drug.loc[
            ~df_rgi_drug['rgi_main.Drug Class'].isna(), 'rgi_main.Drug Class'].str.split(';').apply(
            lambda x: set(y.strip() for y in x))

        if drug_classes is None or len(drug_classes) == 0:
            df_rgi_drug['has_drugs'] = True
        else:
            df_rgi_drug['has_drugs'] = df_rgi_drug['rgi_main.Drug Class'].dropna().apply(
                lambda rgi_drugs: all(drug in rgi_drugs for drug in drug_classes))

        df_rgi_drug['has_drugs'] = df_rgi_drug['has_drugs'].fillna(False)
        df_rgi_drug = df_rgi_drug[['filename', 'has_drugs']].set_index('filename')
        df_rgi_drug = df_rgi_drug.groupby(['filename']).agg('any')

        df_rgi_all = self._df_rgi[['timestamp', 'geo_area_code']].groupby(['filename']).first()
        df_rgi_all = df_rgi_all.merge(df_rgi_drug, on='filename', how='left')

        return df_rgi_all

    def geo_drug_sets_to_counts(self, df_drug_mapping: pd.DataFrame) -> pd.DataFrame:
        df_has_classes = df_drug_mapping.rename(columns={'has_drugs': 'drug_class_count'}).reset_index()
        df_has_classes['drug_class_count'] = df_has_classes['drug_class_count'].apply(lambda x: 1 if x else 0)
        df_has_classes = df_has_classes[['geo_area_code', 'drug_class_count']].set_index('geo_area_code').groupby(
            'geo_area_code').sum()

        return df_has_classes

    def all_drugs_list(self) -> List[str]:
        df_rgi_drug = self._df_rgi[['rgi_main.Drug Class']].replace('', np.nan)
        df_rgi_drug = df_rgi_drug.loc[
            ~df_rgi_drug['rgi_main.Drug Class'].isna(), 'rgi_main.Drug Class'].str.split(';').apply(
            lambda x: set(y.strip() for y in x)).to_frame()

        all_drugs_list = df_rgi_drug['rgi_main.Drug Class'].dropna().tolist()
        all_drugs = set(y for x in all_drugs_list for y in x)

        return all_drugs