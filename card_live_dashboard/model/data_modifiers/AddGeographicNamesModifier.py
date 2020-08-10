import logging

from card_live_dashboard.model.data_modifiers.CardLiveDataModifier import CardLiveDataModifier
from card_live_dashboard.service.GeographicRegionCodesService import GeographicRegionCodesService
from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser

logger = logging.getLogger(__name__)


class AddGeographicNamesModifier(CardLiveDataModifier):

    def __init__(self, region_codes_service: GeographicRegionCodesService):
        """
        Builds a new modifier which will map geographic region codes to names.
        :param region_codes_service: The service object which is used to perform the underlying mapping.
        """
        super().__init__()

        self._region_codes_service = region_codes_service

    def modify(self, data: CardLiveData) -> CardLiveData:
        main_df = data.main_df.copy()
        logger.debug(f'Main df before {main_df}')
        main_df = self._region_codes_service.add_region_standard_names(main_df, 'geo_area_code')
        logger.debug(f'Main df after {main_df}')

        rgi_df = data.rgi_df.copy()
        rgi_kmer_df = data.rgi_kmer_df.copy()
        lmat_df = data.lmat_df.copy()
        mlst_df = data.mlst_df.copy()

        return CardLiveData(main_df=main_df,
                            rgi_parser=RGIParser(rgi_df),
                            rgi_kmer_df=rgi_kmer_df,
                            mlst_df=mlst_df,
                            lmat_df=lmat_df)
