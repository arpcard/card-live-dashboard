from pathlib import Path
from os import path

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader

data_dir = Path(path.dirname(__file__), 'data')


def test_read_one_file():
    loader = CardLiveDataLoader(data_dir.joinpath('data1'))
    data = loader.read_data()

    assert 1 == len(data.main_df)
    assert ['file1'] == data.main_df.index.tolist()
    assert [15] == data.main_df['geo_area_code'].tolist()
    assert 'timestamp' in set(data.main_df.columns.tolist())
    assert 'geo_area_code' in set(data.main_df.columns.tolist())
    assert 'geo_area_name_standard' in set(data.main_df.columns.tolist())
    assert ['Northern Africa'] == data.main_df['geo_area_name_standard'].tolist()
    assert ['Salmonella enterica'] == data.main_df['lmat_taxonomy'].tolist()
    assert ['Enterobacteriaceae'] == data.main_df['rgi_kmer_taxonomy'].tolist()
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

    assert ['Salmonella enterica'] == data.lmat_df['lmat.taxonomy_label'].tolist()
    assert 'timestamp' not in set(data.lmat_df.columns.tolist())
    assert 'geo_area_code' not in set(data.lmat_df.columns.tolist())


def test_read_antarctica_switch():
    loader = CardLiveDataLoader(data_dir.joinpath('data2'))
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
    loader = CardLiveDataLoader(data_dir.joinpath('data1'))
    data = loader.read_or_update_data()

    assert 1 == len(data.main_df)

    new_data = loader.read_or_update_data(data)
    assert data is new_data


def test_read_or_update_data_withupdate():
    loader = CardLiveDataLoader(data_dir.joinpath('data1'))
    data = loader.read_or_update_data()

    assert 1 == len(data.main_df)

    loader = CardLiveDataLoader(data_dir.joinpath('data2'))
    new_data = loader.read_or_update_data(data)
    assert data is not new_data
    assert 2 == len(new_data.main_df)

