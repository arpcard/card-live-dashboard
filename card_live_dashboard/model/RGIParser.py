from __future__ import annotations
from typing import List, Set
from typing import Callable
import re
import logging

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class RGIParser:

    def __init__(self, df_rgi: pd.DataFrame):
        self._df_rgi = df_rgi.copy()
        self._drug_mapping = None

    def select(self, by: str, type: str = None, **kwargs) -> RGIParser:
        """
        Selects data from the RGIParser based on the matched criteria.
        :param by: The method we will use to select by.
        :param type: The type of data to select ('row', or 'file').
        :param kwargs: Additional arguments for the underlying selection method.
        :return: A new RGIParser object which matches the passed criteria.
        """
        if by == 'cutoff':
            return self.select_by_cutoff(type=type, **kwargs)
        elif by == 'drug':
            return self.select_by_drugclass(type=type, **kwargs)
        elif by == 'aro':
            return self.select_by_besthit_aro(type=type, **kwargs)
        else:
            raise Exception(f'Unknown value [by={by}].')

    def select_by(self, func: Callable, type: str = 'row') -> RGIParser:
        """
        Selects data from the underlying dataframe.
        Can be run like:

        rgi_parser.select_by(lambda x: x['column'] == 'value')

        :param func: The select function.
        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :return: A new instance of RGIParser which is a subset of the old instance.
        """
        if type == 'row':
            return RGIParser(self._df_rgi[func(self._df_rgi)].copy())
        elif type == 'file':
            matched_rows = self._df_rgi[func(self._df_rgi)]
            matched_files = set(matched_rows.index)
            return RGIParser(self._df_rgi.loc[matched_files])
        else:
            raise Exception(f'Unknown value [type={type}]. Must be one of ["row", "file"].')

    def select_by_files(self, files) -> RGIParser:
        """
        Selects a subset of data based on the set of files.
        :param files: The set of files to select by.
        :return: Those results on the subset of the passed files.
        """
        return RGIParser(self._df_rgi.loc[files])

    def select_by_cutoff(self, type: str, level: str) -> RGIParser:
        """
        Given a cutoff level, returns an RGIParser object on the subset of data.

        :param level: The level to match (e.g., 'Perfect', 'Strict', 'Loose').
        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :return: An RGIParsesr object on the subset of matched data.
        """
        if level is None or level == 'all':
            return self
        else:
            return self.select_by(type=type, func=lambda x: x['rgi_main.Cut_Off'].str.lower() == level)

    def select_by_drugclass(self, type: str, drug_classes: List[str] = None) -> RGIParser:
        """
        Given a list of drug classes, returns an RGIParser object on the subset of data
        containing all of the passed drug classes.

        :param drug_classes: A list of drug class names to match. An empty list matches everything.
        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :return: An RGIParser object on the subset of matched data.
        """
        df_drugclass = self._get_drugclass_matches(drug_classes)

        if type == 'file':
            filename_matches = df_drugclass[df_drugclass['matches']].index.tolist()
            return RGIParser(self._df_rgi.loc[filename_matches])
        elif type == 'row':
            raise Exception('Unimplemented type [type=row]')
        else:
            raise Exception(f'Unknown value [type={type}]')

    def select_by_besthit_aro(self, type: str, besthit_aro: List[str] = None) -> RGIParser:
        """
        Given a list of Best Hit ARO selections, selects data containing only files with some match.

        :param besthit_aro: A list of Best Hit ARO selections.
        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :return: An RGIParser object on the subset of matched data.
        """
        if besthit_aro is None or len(besthit_aro) == 0:
            return self
        elif type == 'file':
            # Convert 'rgi_main.Best_Hit_ARO' column to a 'Set' of entries. For example
            # | index | rgi_main.Best_Hit_ARO |
            # |-------|-----------------------|
            # | file1 | {'aro1', 'aro2'}      |
            # | file2 | {'aro4', 'aro5'}      |
            collapsed_aro_sets = self._df_rgi.groupby('filename').apply(
                lambda x: set(y for y in x['rgi_main.Best_Hit_ARO'])).to_frame().rename(
                columns={0: 'rgi_main.Best_Hit_ARO'})

            # Set 'matches' column to True if the 'besthit_aro' list is a subset of 'rgi_main.Best_Hit_ARO'
            collapsed_aro_sets['matches'] = collapsed_aro_sets['rgi_main.Best_Hit_ARO'].apply(
                lambda x: set(besthit_aro).issubset(x))

            matches_files = collapsed_aro_sets[collapsed_aro_sets['matches']]
            files = set(matches_files.index.tolist())
            return RGIParser(self._df_rgi.loc[files].copy())
        elif type == 'row':
            raise Exception('Unsupported for type=row')
        else:
            raise Exception(f'Unknown value [type={type}]')

    def _get_drugclass_matches(self, drug_classes: List[str] = None) -> pd.DataFrame:
        """
        Given a list of drug classes, returns a DataFrame indexed by 'filename' with a column 'matches'
        indicating if the particular file contains all of the passed drug classes.

        :param drug_classes: A list of drug class names to match. An empty list matches everything.
        :return: A DataFrame which indicates of a particular file matched all of the passed drugs.
        """
        df_rgi_drug = self._df_rgi.reset_index()[['filename', 'rgi_main.Drug Class']].replace('', np.nan)
        df_rgi_drug['rgi_main.Drug Class'] = df_rgi_drug.loc[
            ~df_rgi_drug['rgi_main.Drug Class'].isna(), 'rgi_main.Drug Class'].str.split(';').apply(
            lambda x: set(y.strip() for y in x))

        if drug_classes is None or len(drug_classes) == 0:
            df_rgi_drug['matches'] = True
        else:
            df_rgi_drug['matches'] = df_rgi_drug['rgi_main.Drug Class'].dropna().apply(
                lambda rgi_drugs: all(drug in rgi_drugs for drug in drug_classes))

        df_rgi_drug['matches'] = df_rgi_drug['matches'].fillna(False)
        df_rgi_drug = df_rgi_drug[['filename', 'matches']].set_index('filename')
        df_rgi_drug = df_rgi_drug.groupby(['filename']).agg('any')

        return df_rgi_drug

    def value_counts(self, col: str) -> pd.DataFrame:
        """
        Given a column, counts the number of files in the underlying dataframe for each category of that column.

        :param col: The column to count by.
        :return: A dataframe with counts by the given column's values.
        """
        counts_frame = self._df_rgi[col].groupby('filename').first().value_counts().to_frame()
        counts_frame = counts_frame.rename(columns={col: 'count'})
        counts_frame.index.name = col
        return counts_frame

    def count_files(self) -> int:
        """
        Counts the number of files contained in the results set.

        :return: The count of the files in the results set.
        """
        return len(self._df_rgi.groupby('filename').first())

    def data_by_file(self) -> pd.DataFrame:
        """
        Gets all data from this dataframe grouped by file.

        :return: All timestamps from this dataframe.
        """
        return self._df_rgi.groupby('filename').first()

    def empty(self) -> bool:
        """
        Whether or not there's any data represented in this object.

        :return: True if there is no data, False otherwise.
        """
        return self._df_rgi.empty

    def files(self) -> Set[str]:
        """
        Returns the set of files in this object.

        :return: The set of files in this object.
        """
        return set(self._df_rgi.index.tolist())

    def explode_column(self, col: str, sep: str = ';') -> pd.DataFrame:
        """
        Explodes a column (e.g., 'rgi_main.Drug Class') in the underlying dataframe based on the passed separator.
        :param col: The column to expand.
        :param sep: The separator character.
        :return: The expanded data frame.
        """
        df_rgi_no_index = self._df_rgi.reset_index()
        exploded_df = df_rgi_no_index[col].replace(r'^\s*$', pd.NA, regex=True).dropna()
        exploded_df = exploded_df.replace(re.compile(f'\\s*{col}\\s*'), col, regex=True).dropna()
        exploded_df = exploded_df.str.split(sep).apply(
                    lambda x: [y.strip() for y in x]).explode().rename(col + '_exploded').to_frame()
        exploded_df = df_rgi_no_index.merge(
            exploded_df, how='left', left_index=True, right_index=True).set_index('filename')

        return exploded_df

    def all_drugs(self) -> Set[str]:
        """
        Gets a set of all possible drug classes.

        :return: A list of all possible drug classes.
        """
        all_drugs = set()
        if not self.empty():
            exploded_df = self.explode_column('rgi_main.Drug Class')['rgi_main.Drug Class_exploded'].dropna()
            if not exploded_df.empty:
                all_drugs = set(exploded_df.tolist())

        return all_drugs

    def all_besthit_aro(self) -> Set[str]:
        """
        Gets a set of all possible Best Hit ARO values.

        :return: A set of all Best Hit ARO values.
        """
        return set(self._df_rgi['rgi_main.Best_Hit_ARO'].dropna().tolist())

    @property
    def df_rgi(self):
        return self._df_rgi
