from os import path
from pathlib import Path

import pandas as pd

from card_live_dashboard.service.GeographicRegionCodesService import GeographicRegionCodesService

region_codes = GeographicRegionCodesService(Path(path.dirname(__file__), '..', '..', '..',
                                                 'service', 'data', 'UN-M49', 'UNSD-Methodology.csv'))


def test_add_region_standard_names():
    data = pd.DataFrame(
        columns=['filename', 'color', 'region_codes'],
        data=[['file1', 'red', 15],  # Nothern Africa
              ['file2', 'green', 143],  # Central Asia
              ['file3', 'green', 143],  # Central Asia
              ]
    ).set_index('filename')

    new_data = region_codes.add_region_standard_names(data, 'region_codes')
    assert 3 == len(new_data)
    assert ['file1', 'file2', 'file3'] == new_data.index.tolist()
    assert ['red', 'green', 'green'] == new_data['color'].tolist()
    assert ['Northern Africa', 'Central Asia', 'Central Asia'] == new_data['geo_area_name_standard'].tolist()
    assert [15, 143, 143] == new_data['region_codes'].tolist()
    assert set(data.columns.tolist()).union(
        {'geo_area_name_standard', 'geo_area_toplevel_m49code'}) == set(new_data.columns.tolist())


def test_add_region_standard_names_default_missing_mappings():
    data = pd.DataFrame(
        columns=['filename', 'color', 'region_codes'],
        data=[['file1', 'red', 15],  # Nothern Africa
              ['file2', 'blue', 0],
              ['file3', 'green', -1],
              ['file4', 'green', -2],
              ['file5', 'green', 223],
              ['file6', 'yellow', 10000],
              ]
    ).set_index('filename')

    new_data = region_codes.add_region_standard_names(data, 'region_codes')
    assert 6 == len(new_data)
    assert ['file1', 'file2', 'file3', 'file4', 'file5', 'file6'] == new_data.index.tolist()
    assert ['red', 'blue', 'green', 'green', 'green', 'yellow'] == new_data['color'].tolist()
    assert ['Northern Africa', 'Multiple regions', 'N/A', 'N/A',
            'Eastern Asia (excluding Japan and China)',
            'N/A [code=10000]'] == new_data['geo_area_name_standard'].tolist()
    assert {False} == set(new_data['geo_area_name_standard'].isna().tolist())
    assert [15, 0, -1, -2, 223, 10000] == new_data['region_codes'].tolist()
    assert set(data.columns.tolist()).union(
        {'geo_area_name_standard', 'geo_area_toplevel_m49code'}) == set(new_data.columns.tolist())


def test_add_region_standard_names_no_missing_mappings():
    region_codes = GeographicRegionCodesService(Path(path.dirname(__file__), '..', '..', '..',
                                                     'service', 'data', 'UN-M49', 'UNSD-Methodology.csv'),
                                                use_default_additional_mappings=False)

    data = pd.DataFrame(
        columns=['filename', 'color', 'region_codes'],
        data=[['file1', 'red', 15],  # Nothern Africa
              ['file2', 'green', -1],
              ['file3', 'green', 0],
              ]
    ).set_index('filename')

    new_data = region_codes.add_region_standard_names(data, 'region_codes')
    assert 3 == len(new_data)
    assert ['file1', 'file2', 'file3'] == new_data.index.tolist()
    assert ['red', 'green', 'green'] == new_data['color'].tolist()
    assert 'Northern Africa' == new_data.at['file1', 'geo_area_name_standard']
    assert [False, True, True] == new_data['geo_area_name_standard'].isna().tolist()
    assert [15, -1, 0] == new_data['region_codes'].tolist()
    assert set(data.columns.tolist()).union(
        {'geo_area_name_standard', 'geo_area_toplevel_m49code'}) == set(new_data.columns.tolist())
