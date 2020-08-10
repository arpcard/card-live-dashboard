import abc

from card_live_dashboard.model.CardLiveData import CardLiveData

"""
Abstract class used to implement arbitrary modifiers to data stored in CardLiveData.
"""


class CardLiveDataModifier(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def modify(self, data: CardLiveData) -> CardLiveData:
        """
        The method to implement to modify CardLiveData.
        :param data: The CardLiveData to modify.
        :return: A new CardLiveData instance that has been modified.
        """
        pass
