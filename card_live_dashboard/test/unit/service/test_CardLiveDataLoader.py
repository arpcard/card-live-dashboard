from pathlib import Path
from os import path

from card_live_dashboard.service.CardLiveDataLoader import CardLiveDataLoader

data_dir = Path(path.dirname(__file__), 'data')


def test_read_one_file():
    loader = CardLiveDataLoader(data_dir.joinpath('data1'))
    data = loader.read_data()

    assert 1 == len(data.main_df)
    assert ['file1'] == data.main_df.index.tolist()
    assert [10] == data.main_df['geo_area_code'].tolist()
    assert ['Perfect'] == data.rgi_df['rgi_main.Cut_Off'].tolist()
    assert ['macrolide antibiotic; cephalosporin'] == data.rgi_df['rgi_main.Drug Class'].tolist()
    assert ['Salmonella enterica (chromosome)'] == data.rgi_kmer_df['rgi_kmer.CARD*kmer Prediction'].tolist()
    assert ['senterica'] == data.mlst_df['mlst.scheme'].tolist()
    assert ['Salmonella enterica'] == data.lmat_df['lmat.taxonomy_label'].tolist()
