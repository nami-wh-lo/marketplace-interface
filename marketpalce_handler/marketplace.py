from abc import ABC, abstractmethod


class Marketplace(ABC):
    @abstractmethod
    def refresh_stock(self, ms_id, value):
        pass

    @abstractmethod
    def refresh_price(self, ms_id, value):
        pass

    @abstractmethod
    def refresh_status(self, ms_id, value):
        pass

    @abstractmethod
    def refresh_stocks(self, ids: list[int], values: list[int]):
        pass

    @abstractmethod
    def refresh_prices(self, ids: list[int], values: list[int]):
        pass

    @abstractmethod
    def refresh_statuses(self, ids: list[int], values: list[str]):
        pass
