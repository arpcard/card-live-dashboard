from typing import List
import pandas as pd
from pathlib import Path
import json
from os import path


class CardLiveDataLoader:
    JSON_DATA_FIELDS = [
        'rgi_main',
        'rgi_kmer',
        'mlst',
        'lmat',
    ]

    def __init__(self, card_live_dir: Path):
        self._directory = card_live_dir

        self._main_df = None
        self._rgi_df = None
        self._rgi_kmer_df = None
        self._mlst_df = None
        self._lmat_df = None

        if self._directory == None:
            raise Exception('Invalid value [card_live_dir=None]')
        elif not self._directory.exists():
            raise Exception(f'Data directory [card_live_dir={card_live_dir}] does not exist')
        else:
            self.read_data(self._directory)

    def read_data(self, directory: Path):
        input_files = Path(directory).glob('*')
        json_data = []
        for input_file in input_files:
            filename = path.basename(input_file)
            with open(input_file) as f:
                json_obj = json.load(f)
                json_obj['filename'] = filename
                json_data.append(json_obj)

        self._full_df = pd.json_normalize(json_data).set_index('filename')
        self._full_df = self._replace_empty_list_na(self._full_df, self.JSON_DATA_FIELDS)
        self._full_df = self._create_analysis_valid_column(self._full_df, self.JSON_DATA_FIELDS)
        self._full_df['timestamp'] = pd.to_datetime(self._full_df['timestamp'])
        self._main_df = self._full_df.drop(columns=self.JSON_DATA_FIELDS)

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
            df.loc[~df[col].isna() & ~(df['analysis_valid'] == 'None'), 'analysis_valid'] = df[
                                                                                                'analysis_valid'] + ' and ' + col
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

    @property
    def main_df(self) -> pd.DataFrame:
        return self._main_df

    @property
    def rgi_df(self) -> pd.DataFrame:
        if self._rgi_df is None:
            self._rgi_df = self._expand_column(self._full_df, 'rgi_main', na_char='n/a').drop(
                columns=self.JSON_DATA_FIELDS)

        return self._rgi_df

    @property
    def rgi_kmer_df(self) -> pd.DataFrame:
        if self._rgi_kmer_df is None:
            self._rgi_kmer_df = self._expand_column(self._full_df, 'rgi_kmer', na_char='n/a').drop(
                columns=self.JSON_DATA_FIELDS)

        return self._rgi_kmer_df

    @property
    def mlst_df(self) -> pd.DataFrame:
        if self._mlst_df is None:
            self._mlst_df = self._expand_column(self._full_df, 'mlst', na_char='-').drop(columns=self.JSON_DATA_FIELDS)

        return self._mlst_df

    @property
    def lmat_df(self) -> pd.DataFrame:
        if self._lmat_df is None:
            self._lmat_df = self._expand_column(self._full_df, 'lmat', na_char='n/a').drop(
                columns=self.JSON_DATA_FIELDS)

        return self._lmat_df
