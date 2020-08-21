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
        if len(self._df_rgi) == 0:
            return self
        elif by == 'cutoff':
            return self.select_by_cutoff(type=type, **kwargs)
        elif by == 'drug':
            return self.select_by_elements_in_column_split(type=type, column='rgi_main.Drug Class', **kwargs)
        elif by == 'amr_gene':
            return self.select_by_elements_in_column(type=type, column='rgi_main.Best_Hit_ARO', **kwargs)
        elif by == 'resistance_mechanism':
            return self.select_by_elements_in_column_split(type=type, column='rgi_main.Resistance Mechanism', **kwargs)
        elif by == 'amr_gene_family':
            return self.select_by_elements_in_column_split(type=type, column='rgi_main.AMR Gene Family', **kwargs)
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
        return self.select_by_elements_in_column_split(type=type, column='rgi_main.Drug Class', elements=drug_classes)

    def select_by_elements_in_column_split(self, type: str, column: str, sep: str = ';',
                                           elements: List[str] = None) -> RGIParser:
        """
        Given a list of elements and a column, returns an RGIParser object on the subset of data
        containing all of the passed elements after splitting the column by the given split string.

        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :param column: The column to select on.
        :param sep: The separator string.
        :param elements: A list of drug class names to match. An empty list matches everything.
        :return: An RGIParser object on the subset of matched data.
        """
        if type == 'file':
            matched_files = self._get_column_matches_split(column=column, sep=sep, elements=elements)
            return RGIParser(self._df_rgi.loc[matched_files])
        elif type == 'row':
            raise Exception('Unimplemented type [type=row]')
        else:
            raise Exception(f'Unknown value [type={type}]')

    def select_by_elements_in_column(self, type: str, column: str, elements: List[str] = None) -> RGIParser:
        """
        Given a list of elements in a column, selects data containing only files with some match.

        :param type: The type of results to select.
            'row' means that the function is used to select rows in the data frame.
            'file' means that all data for files matching the criteria are selected.
        :param column: The column in the data frame to select by.
        :param elements: A list of elements to select by.
        :return: An RGIParser object on the subset of matched data.
        """
        if elements is None or len(elements) == 0:
            return self
        elif type == 'file':
            # Convert 'column' column to a 'Set' of entries. For example, if column is 'rgi_main.Best_Hit_ARO' gives
            # | index | rgi_main.Best_Hit_ARO   |
            # |-------|-------------------------|
            # | file1 | {'gene1', 'gene2'}      |
            # | file2 | {'gene4', 'gene5'}      |
            collapsed_elements_sets = self._df_rgi.groupby('filename').apply(
                lambda x: set(y for y in x[column])).to_frame().rename(
                columns={0: column})

            # Set 'matches' column to True if the 'elements' list is a subset of 'column'
            collapsed_elements_sets['matches'] = collapsed_elements_sets[column].apply(
                lambda x: set(elements).issubset(x))

            matches_files = collapsed_elements_sets[collapsed_elements_sets['matches']]
            files = set(matches_files.index.tolist())
            return RGIParser(self._df_rgi.loc[files].copy())
        elif type == 'row':
            raise Exception('Unsupported for type=row')
        else:
            raise Exception(f'Unknown value [type={type}]')

    def _get_column_matches_split(self, column: str, sep: str = ';', elements: List[str] = None) -> Set[str]:
        """
        Given a list of elements and a column, returns a set of files that contain all the elements after splitting
         by the passed separator.

        :param column: The column to search through.
        :param sep: The separator string to split items in the column.
        :param elements: The list of elements to match.
        :return: A list of matching files.
        """
        if elements is None or len(elements) == 0:
            return self.files()
        else:
            elements_set = set(elements)

            df_rgi_new = self.explode_column(column, sep=sep)[f'{column}_exploded'].dropna()
            df_rgi_new = df_rgi_new.groupby('filename').apply(lambda x: set(y for y in x)).to_frame()
            df_rgi_new['match'] = df_rgi_new[f'{column}_exploded'].apply(lambda x: elements_set.issubset(x))

            return df_rgi_new[df_rgi_new['match']].index.tolist()

    def get_column_values(self, data_type: str) -> pd.Series:
        """
        Gets the values of a column given a particular data type.
        :param data_type: The data type to select.
        :return: The values of the column.
        """
        additional_columns = ['geo_area_name']

        if data_type == 'drug_class':
            totals_df = self.explode_column('rgi_main.Drug Class')['rgi_main.Drug Class_exploded']
        elif data_type == 'amr_gene_family':
            totals_df = self.explode_column('rgi_main.AMR Gene Family')['rgi_main.AMR Gene Family_exploded']
        elif data_type == 'resistance_mechanism':
            totals_df = self.explode_column('rgi_main.Resistance Mechanism')['rgi_main.Resistance Mechanism_exploded']
        elif data_type == 'amr_gene':
            totals_df = self._df_rgi['rgi_main.Best_Hit_ARO']
        else:
            raise Exception(f'Unknown value [type_value={data_type}]')

        return totals_df

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
        return self._all_by_column_split('rgi_main.Drug Class')

    def all_amr_genes(self) -> Set[str]:
        """
        Gets a set of all possible AMR genes (Best Hit ARO values).

        :return: A set of all AMR genes (Best Hit ARO values).
        """
        return self._all_by_column('rgi_main.Best_Hit_ARO')

    def all_resistance_mechanisms(self) -> Set[str]:
        """
        Gets a set of all possible resistance mechanisms.

        :return: A set of all resistance mechanisms.
        """
        return self._all_by_column_split('rgi_main.Resistance Mechanism')


    def all_amr_gene_family(self) -> Set[str]:
        """
        Gets a set of all possible resistance mechanisms.

        :return: A set of all resistance mechanisms.
        """
        return self._all_by_column_split('rgi_main.AMR Gene Family')


    def _all_by_column(self, col: str) -> Set[str]:
        """
        Gets a set of all possible entries by column.

        :param col: The column.
        :return: A set of all possible entries in the column.
        """
        return set(self._df_rgi[col].dropna().tolist())

    def _all_by_column_split(self, column: str, sep: str = ';') -> Set[str]:
        """
        Gets a set of all possible elements after splitting by the passed string.

        :param column: The column to search through.
        :param sep: The separator string.
        :return: A set of all possible elements.
        """
        all_elements = set()
        if not self.empty():
            exploded_df = self.explode_column(column, sep=sep)[f'{column}_exploded'].dropna()
            if not exploded_df.empty:
                all_elements = set(exploded_df.tolist())

        return all_elements

    @property
    def df_rgi(self):
        return self._df_rgi
