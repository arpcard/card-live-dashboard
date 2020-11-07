from os import path
from pathlib import Path

from card_live_dashboard.service.GeographicRegionCodesService import GeographicRegionCodesService

region_codes = GeographicRegionCodesService(Path(path.dirname(__file__), 'data', 'UN-M49', 'UNSD-Methodology.csv'))
