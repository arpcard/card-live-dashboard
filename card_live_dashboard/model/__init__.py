from card_live_dashboard.model.GeographicSummaries import GeographicSummaries
from card_live_dashboard.service import region_codes

world = region_codes.get_un_m49_regions_naturalearth()
geographic_summaries = GeographicSummaries(region_codes)
