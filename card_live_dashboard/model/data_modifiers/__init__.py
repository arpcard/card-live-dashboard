import numpy as np

from card_live_dashboard.model.data_modifiers.AntarcticaNAModifier import AntarcticaNAModifier
from card_live_dashboard.model.data_modifiers.AddGeographicNamesModifier import AddGeographicNamesModifier
from card_live_dashboard.service import region_codes

antarctica_modifier = AntarcticaNAModifier(np.datetime64('2020-07-20'))
geo_names_modifier = AddGeographicNamesModifier(region_codes)
