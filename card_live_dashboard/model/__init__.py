from pathlib import Path
from os import path

from card_live_dashboard.model.GeographicRegionCodes import GeographicRegionCodes
from card_live_dashboard.model.GeographicSummaries import GeographicSummaries

region_codes = GeographicRegionCodes(Path(path.dirname(__file__), 'data', 'UN-M49', 'UNSD-Methodology.csv'))
world = region_codes.get_un_m49_regions_naturalearth()
geographic_summaries = GeographicSummaries(region_codes)