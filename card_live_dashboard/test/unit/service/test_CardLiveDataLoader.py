import io
import zipfile
from os import path
from pathlib import Path
from typing import List

import numpy as np

from card_live_dashboard.model.data_modifiers.AddGeographicNamesModifier import AddGeographicNamesModifier
from card_live_dashboard.model.data_modifiers.AntarcticaNAModifier import AntarcticaNAModifier
from card_live_dashboard.service import region_codes
from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader

data_dir = Path(path.dirname(__file__), 'data')


def test_read_one_file():
    loader = CardLiveDataLoader(data_dir / 'data1')
    loader.add_data_modifiers([
        AddGeographicNamesModifier(region_codes),
    ])
    data = loader.read_data()

    assert 1 == len(data.main_df)
    assert ['file1'] == data.main_df.index.tolist()
    assert [15] == data.main_df['geo_area_code'].tolist()
    assert 'timestamp' in set(data.main_df.columns.tolist())
    assert 'geo_area_code' in set(data.main_df.columns.tolist())
    assert 'geo_area_name_standard' in set(data.main_df.columns.tolist())
    assert ['Northern Africa'] == data.main_df['geo_area_name_standard'].tolist()
    assert 'matches' not in set(data.main_df.columns.tolist())

    assert 2 == len(data.rgi_df)
    assert ['Perfect', 'Strict'] == data.rgi_df['rgi_main.Cut_Off'].tolist()
    assert ['macrolide antibiotic; cephalosporin', 'macrolide antibiotic; cephalosporin'] == data.rgi_df[
        'rgi_main.Drug Class'].tolist()
    assert 'timestamp' not in set(data.rgi_df.columns.tolist())
    assert 'geo_area_code' not in set(data.rgi_df.columns.tolist())

    assert ['Enterobacteriaceae (chromosome)'] == data.rgi_kmer_df['rgi_kmer.CARD*kmer Prediction'].tolist()
    assert 'timestamp' not in set(data.rgi_kmer_df.columns.tolist())
    assert 'geo_area_code' not in set(data.rgi_kmer_df.columns.tolist())

    assert ['senterica'] == data.mlst_df['mlst.scheme'].tolist()
    assert 'timestamp' not in set(data.mlst_df.columns.tolist())
    assert 'geo_area_code' not in set(data.mlst_df.columns.tolist())

    assert 'timestamp' not in set(data.lmat_df.columns.tolist())
    assert 'geo_area_code' not in set(data.lmat_df.columns.tolist())


def test_read_antarctica_switch():
    loader = CardLiveDataLoader(data_dir / 'data2')
    loader.add_data_modifiers([
        AntarcticaNAModifier(np.datetime64('2020-07-20')),
        AddGeographicNamesModifier(region_codes),
    ])
    data = loader.read_data()

    assert 2 == len(data.main_df)
    assert ['file1', 'file2'] == data.main_df.index.tolist()
    assert [-10, 10] == data.main_df['geo_area_code'].tolist()
    assert ['N/A', 'Antarctica'] == data.main_df['geo_area_name_standard'].tolist()
    assert ['Perfect', 'Strict'] == data.rgi_df['rgi_main.Cut_Off'].tolist()
    assert ['macrolide antibiotic; cephalosporin', 'macrolide antibiotic'] == data.rgi_df[
        'rgi_main.Drug Class'].tolist()
    assert ['Enterobacteriaceae (chromosome)', 'Salmonella enterica (chromosome)'] == data.rgi_kmer_df[
        'rgi_kmer.CARD*kmer Prediction'].tolist()
    assert ['senterica', 'senterica'] == data.mlst_df['mlst.scheme'].tolist()
    assert ['Salmonella enterica', 'Salmonella enterica'] == data.lmat_df['lmat.taxonomy_label'].tolist()


def test_read_or_update_data_noupdate():
    loader = CardLiveDataLoader(data_dir / 'data1')
    data = loader.read_or_update_data()

    assert 1 == len(data.main_df)

    new_data = loader.read_or_update_data(data)
    assert data is new_data


def test_read_or_update_data_withupdate():
    loader = CardLiveDataLoader(data_dir / 'data1')
    data = loader.read_or_update_data()

    assert 1 == len(data.main_df)

    loader = CardLiveDataLoader(data_dir / 'data2')
    new_data = loader.read_or_update_data(data)
    assert data is not new_data
    assert 2 == len(new_data.main_df)


def write_zip_to_memory_file(loader: CardLiveDataLoader, files: List[str]) -> io.BytesIO:
    """
    Helper method to generate an in-memory zip archive for testing zipping of files.
    :param loader: The CardLiveDataLoader.
    :param files: The files to zip.
    :return: An in-memory file containing the zipped data.
    """
    memory_archive = io.BytesIO()
    for chunk in loader.data_archive_generator(files):
        memory_archive.write(chunk)
    memory_archive.seek(0)

    return memory_archive


def test_data_archive_generator_one_file():
    loader = CardLiveDataLoader(data_dir / 'data2')
    memory_archive = write_zip_to_memory_file(loader, ['file1'])

    with zipfile.ZipFile(memory_archive, 'r') as zf:
        assert {'card_live/file1'} == set(zf.namelist())

    memory_archive.close()


def test_data_archive_generator_both_files():
    loader = CardLiveDataLoader(data_dir / 'data2')
    memory_archive = write_zip_to_memory_file(loader, ['file1', 'file2'])

    with zipfile.ZipFile(memory_archive, 'r') as zf:
        assert {'card_live/file1', 'card_live/file2'} == set(zf.namelist())

    memory_archive.close()


def test_data_archive_generator_skip_invalid_file():
    loader = CardLiveDataLoader(data_dir / 'data3')
    memory_archive = write_zip_to_memory_file(loader, ['file1', 'file-invalid'])

    with zipfile.ZipFile(memory_archive, 'r') as zf:
        assert {'card_live/file1'} == set(zf.namelist())

    memory_archive.close()
