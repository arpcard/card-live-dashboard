from typing import List, Set
from typing import Callable
from datetime import datetime

import pandas as pd
import numpy as np


class RGIParser:

    def __init__(self, df_rgi: pd.DataFrame):
        self._df_rgi = df_rgi
        self._drug_mapping = None

    def filter_by(self, func: Callable):
        """
        Applies a filter to the underlying dataframe to select specific columns.
        Can be run like:

        rgi_parser.filter_by(lambda x: x['column'] == 'value')

        :param func: The filter function.
        :return: A new instance of RGIParser which is a subset of the old instance.
        """
        return RGIParser(self._df_rgi[func(self._df_rgi)].copy())

    def filter_by_cutoff(self, level: str):
        """
        Given a cutoff level, returns an RGIParser object on the subset of data with files
        containing RGI hits at that level.

        :param level: The level to match (e.g., 'Perfect', 'Strict', 'Loose').
        :return: An RGIParsesr object on the subset of matched data.
        """
        if level is None or level == 'all':
            return self
        else:
            return self.filter_by(lambda x: x['rgi_main.Cut_Off'].str.lower() == level)

    def filter_by_drugclass(self, drug_classes: List[str] = None):
        """
        Given a list of drug classes, returns an RGIParser object on the subset of data with files
        containing all of the passed drug classes.

        :param drug_classes: A list of drug class names to match. An empty list matches everything.
        :return: An RGIParser object on the subset of matched data.
        """
        df_drugclass = self._get_drugclass_matches(drug_classes)
        filename_matches = set(df_drugclass[df_drugclass['matches']].index.tolist())

        return RGIParser(self._df_rgi.loc[filename_matches])

    def filter_by_besthit_aro(self, besthit_aro: List[str] = None):
        """
        Given a list of Best Hit ARO selections, filters this RGIParser object to those containing only files with some match.

        :param besthit_aro: A list of Best Hit ARO selections.
        :return: An RGIParser object on the subset of matched data.
        """
        if besthit_aro is None or len(besthit_aro) == 0:
            return self
        else:
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

    def filter_by_time(self, start: datetime, end: datetime):
        """
        Filters the data to be within the start and end time periods.

        :param start: The start time.
        :param end: The end time.

        :return: An RGIParser object on the subset of matched data.
        """
        return self.filter_by(lambda x: (x['timestamp'] >= start) & (x['timestamp'] <= end))

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

    def timestamps(self) -> pd.DataFrame:
        """
        Gets all timestamps from this dataframe.

        :return: All timestamps from this dataframe.
        """
        return self._df_rgi.groupby('filename').first()[['timestamp']]

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

    def all_drugs(self) -> Set[str]:
        """
        Gets a set of all possible drug classes.

        :return: A list of all possible drug classes.
        """
        df_rgi_drug = self._df_rgi[['rgi_main.Drug Class']].replace('', np.nan)
        df_rgi_drug = df_rgi_drug.loc[
            ~df_rgi_drug['rgi_main.Drug Class'].isna(), 'rgi_main.Drug Class'].str.split(';').apply(
            lambda x: set(y.strip() for y in x)).to_frame()

        all_drugs_list = df_rgi_drug['rgi_main.Drug Class'].dropna().tolist()

        # Store as 'set' first to remove duplicates
        all_drugs = set(y for x in all_drugs_list for y in x)

        return all_drugs

    def all_besthit_aro(self) -> Set[str]:
        """
        Gets a set of all possible Best Hit ARO values.

        :return: A set of all Best Hit ARO values.
        """
        return set(self._df_rgi['rgi_main.Best_Hit_ARO'].dropna().tolist())