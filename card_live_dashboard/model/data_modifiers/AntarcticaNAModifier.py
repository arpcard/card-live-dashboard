import numpy as np

from card_live_dashboard.model.CardLiveData import CardLiveData
from card_live_dashboard.model.RGIParser import RGIParser
from card_live_dashboard.model.data_modifiers.CardLiveDataModifier import CardLiveDataModifier


class AntarcticaNAModifier(CardLiveDataModifier):

    def __init__(self, date_threshold: np.datetime64):
        """
        Builds a new AntarcticaNAModifier with the given date threshold.
        This replaces the Antarctica geo code (10) with an N/A geo code (-10) for dates before the threshold.
        This is because for CARD:Live, initially Antarctica was the default option given to users.
        So, much of the data stored in CARD:Live had 'Antarctica' set as the geographic region when what
        was intended was 'N/A'. This method fixes the issue.
        :param date_threshold: The date threshold before which Antarctica is changed to N/A.
        """
        super().__init__()

        self._date_threshold = date_threshold

    def modify(self, data: CardLiveData) -> CardLiveData:
        na_code = -10

        main_df = data.main_df.copy()
        main_df.loc[(main_df['geo_area_code'] == 10) &
                    (main_df['timestamp'] < self._date_threshold), 'geo_area_code'] = na_code

        rgi_df = data.rgi_df.copy()
        rgi_kmer_df = data.rgi_kmer_df.copy()
        lmat_df = data.lmat_df.copy()
        mlst_df = data.mlst_df.copy()

        return CardLiveData(main_df=main_df,
                            rgi_parser=RGIParser(rgi_df),
                            rgi_kmer_df=rgi_kmer_df,
                            mlst_df=mlst_df,
                            lmat_df=lmat_df)
