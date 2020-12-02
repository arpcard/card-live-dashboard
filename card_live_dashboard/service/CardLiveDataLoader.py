from __future__ import annotations

import json
import logging
from os import path, listdir
from pathlib import Path
from typing import Generator
from typing import List, Set, Union

import pandas as pd
import zipstream

from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser
from card_live_dashboard.model.data_modifiers.CardLiveDataModifier import CardLiveDataModifier

logger = logging.getLogger(__name__)


class CardLiveDataLoader:
    JSON_DATA_FIELDS = [
        'rgi_main',
        'rgi_kmer',
        'mlst',
        'lmat',
    ]

    OTHER_TABLE_DROP_FIELDS = JSON_DATA_FIELDS + [
        'timestamp',
        'geo_area_code',
    ]

    def __init__(self, card_live_data: Path):
        self._directory = card_live_data

        if self._directory is None:
            raise Exception('Invalid value [card_live_data=None]')

        self._data_modifiers = []

    def add_data_modifiers(self, data_modifiers: List[CardLiveDataModifier]) -> None:
        """
        Adds a list of new objects used to apply post modifications to the data.
        :param data_modifiers: A list of data modifier objects.
        :return: None.
        """
        self._data_modifiers.extend(data_modifiers)

    def read_or_update_data(self, existing_data: CardLiveData = None) -> CardLiveData:
        """
        Given an existing data object, updates the data object with any new files.
        :param existing_data: The existing data object (None if all data should be read).
        :return: The original (unmodified) data object if no updates, otherwise a new data object with additional data.
        """
        input_files = [Path(self._directory) / f for f in listdir(self._directory) if
                       path.isfile(Path(self._directory) / f)]
        input_files.sort()

        if existing_data is None:
            return self.read_data(input_files)
        elif not self._directory.exists():
            raise Exception(f'Data directory [card_live_dir={self._directory}] does not exist')
        else:
            existing_files = existing_data.files()
            input_files_set = {p.name for p in input_files}

            files_new = input_files_set - existing_files

            # If no new files have been found
            if len(files_new) == 0:
                logger.debug(f'Data has not changed from {len(input_files_set)} samples, not updating')
                return existing_data
            else:
                logger.info(f'{len(files_new)} additional samples found.')
                return self.read_data(input_files)

    def read_data(self, input_files: list = None) -> CardLiveData:
        """
        Reads in the data and constructs a CardLiveData object.
        :param input_files: The (optional) list of input files. Leave as None to read from the configured directory.
                            The optional list is used so I don't have to re-read the directory after running
                            read_or_update_data().
        :return: The CardLiveData object.
        """
        if input_files is None:
            if not self._directory.exists():
                raise Exception(f'Data directory [card_live_dir={self._directory}] does not exist')
            else:
                input_files = [Path(self._directory) / f for f in listdir(self._directory) if
                               path.isfile(Path(self._directory) / f)]
                input_files.sort()

        json_data = []
        for input_file in input_files:
            filename = path.basename(input_file)
            with open(input_file) as f:
                try:
                    json_obj = json.load(f)
                    json_obj['filename'] = filename
                    json_data.append(json_obj)
                except Exception:
                    logger.warning(f'File [{input_file}] is not a proper CARD:Live JSON file, skipping file.')

        full_df = pd.json_normalize(json_data).set_index('filename')
        full_df = self._replace_empty_list_na(full_df, self.JSON_DATA_FIELDS)
        full_df = self._create_analysis_valid_column(full_df, self.JSON_DATA_FIELDS)
        full_df['timestamp'] = pd.to_datetime(full_df['timestamp'])

        main_df = full_df.drop(columns=self.JSON_DATA_FIELDS)
        rgi_df = self._expand_column(full_df, 'rgi_main', na_char='n/a').drop(
            columns=self.OTHER_TABLE_DROP_FIELDS)
        rgi_kmer_df = self._expand_column(full_df, 'rgi_kmer', na_char='n/a').drop(
            columns=self.OTHER_TABLE_DROP_FIELDS)
        mlst_df = self._expand_column(full_df, 'mlst', na_char='-').drop(
            columns=self.OTHER_TABLE_DROP_FIELDS)
        lmat_df = self._expand_column(full_df, 'lmat', na_char='n/a').drop(
            columns=self.OTHER_TABLE_DROP_FIELDS)

        data = CardLiveData(main_df=main_df,
                            rgi_parser=RGIParser(rgi_df),
                            rgi_kmer_df=rgi_kmer_df,
                            mlst_df=mlst_df,
                            lmat_df=lmat_df)

        # apply data modifiers
        for modifier in self._data_modifiers:
            data = modifier.modify(data)

        return data

    def data_archive_generator(self, file_names: Union[List[str], Set[str]]) -> Generator[bytes, None, None]:
        """
        Get the CARD:Live JSON files as a zipstream generator
        (code derived from https://pypi.org/project/zipstream-new/).
        :param file_names: The file names to load into the archive.
        :return: A generator which allows streaming of the zip file contents.
        """
        zf = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

        for file in file_names:
            file_path = path.join(self._directory, file)
            valid_file = False
            with open(file_path) as f:
                try:
                    json_obj = json.load(f)
                    valid_file = 'rgi_main' in json_obj
                except Exception:
                    valid_file = False
            if valid_file:
                zf.write(file_path, arcname=f'card_live/{file}')
                yield from zf.flush()
            else:
                logger.warning((f'File [{file_path}] is not a proper CARD:Live JSON file, '
                                'skipping file in download request.'))

        yield from zf

    def _rows_with_empty_list(self, df: pd.DataFrame, col_name: str):
        empty_rows = {}
        for index, row in df.iterrows():
            empty_rows[index] = (len(row[col_name]) == 0)
        return pd.Series(empty_rows)

    def _replace_empty_list_na(self, df: pd.DataFrame, cols: List[str]):
        dfnew = df.copy()
        for column in cols:
            empty_rows = self._rows_with_empty_list(df, column)
            dfnew.loc[empty_rows, column] = None
        return dfnew

    def _create_analysis_valid_column(self, df: pd.DataFrame, analysis_cols: List[str]):
        df = df.copy()
        df['analysis_valid'] = 'None'
        for col in analysis_cols:
            df.loc[~df[col].isna() & ~(df['analysis_valid'] == 'None'), 'analysis_valid'] = df['analysis_valid'] \
                                                                                            + ' and ' + col
            df.loc[~df[col].isna() & (df['analysis_valid'] == 'None'), 'analysis_valid'] = col
        return df.replace(' and '.join(self.JSON_DATA_FIELDS), 'all')

    def _expand_column(self, df: pd.DataFrame, column: str, na_char: str = None):
        """
        Expands a particular column in the dataframe from a list of dictionaries to columns.
        That is expands a column like 'col' => [{'key1': 'value1', 'key2': 'value2'}] to a dataframe
          with new columns 'col.key1', 'col.key2'.

        :param df: The dataframe to use.
        :param column: The name of the column to explode.
        :param na_char: A character to replace with NA (defaults to no replacement).

        :return: A new dataframe with the new columns appended onto it.
        """
        exploded_columns = df[column].explode().apply(pd.Series).add_prefix(f'{column}.')
        if na_char is not None:
            exploded_columns.replace({na_char: None}, inplace=True)
        merged_df = pd.merge(df, exploded_columns, how='left', on=df.index.name)

        return merged_df
