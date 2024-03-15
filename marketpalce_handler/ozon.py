from typing import List

import requests
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from .collector import Collector
from .marketplace import Marketplace
from .logger import get_logger
from .config import settings
from .utils import get_chunks
from .validators import (
    validate_id_and_value,
    validate_ids_and_values,
    validate_warehouse_id,
    validate_warehouse_ids,
)


class Ozon(Marketplace):
    def __init__(
        self,
        client_id: str,
        api_key: str,
        collector_api_key: str,
        collector_url: str,
        session: Session = requests.Session(),
    ):
        self._collector_service = Collector(collector_api_key, collector_url)
        self._logger = get_logger()
        self._session = session
        retries = Retry(
            total=3,
            backoff_factor=0.5,
        )
        self._session.mount("https://", HTTPAdapter(max_retries=retries))
        self._session.headers.update(
            {
                "Client-Id": client_id,
                "Api-Key": api_key,
            }
        )
        self._logger.info("Ozon marketplace is initialised")

    def get_prices(self, ms_ids: list[str]) -> dict:
        mapped_data = self._collector_service.get_mapped_data(ms_ids)
        ozon_ids = [item.offer_id for item in mapped_data]
        resp = self._session.post(
            f"{settings.ozon_api_url}v4/product/info/prices",
            json={
                "filter": {"offer_id": ozon_ids, "visibility": "ALL"},
                "limit": "1000",
            },
        )
        return resp.json()

    @validate_id_and_value
    def refresh_price(self, ms_id: str, value: int):
        mapped_data = self._collector_service.get_mapped_data([ms_id])
        offer_id = mapped_data[0].offer_id
        resp = self._session.post(
            f"{settings.ozon_api_url}v1/product/import/prices",
            json={"prices": [{"offer_id": offer_id, "price": str(value)}]},
        )
        return resp.json()

    @validate_ids_and_values
    def refresh_prices(self, ms_ids: List[str], values: List[int]):
        mapped_data = self._collector_service.get_mapped_data(ms_ids)
        ids_map = {item.ms_id: item.offer_id for item in mapped_data}
        if len(ms_ids) > settings.OZONE_PRICE_LIMIT:
            chunks_ids, chunks_values = get_chunks(
                ms_ids, values, settings.OZONE_PRICE_LIMIT
            )
            for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                self.refresh_prices(chunk_ids, chunk_values)

        prices = []
        for ms_id, value in zip(ms_ids, values):
            prices.append({"offer_id": ids_map[ms_id], "price": str(value)})
        return self._session.post(
            f"{settings.ozon_api_url}v1/product/import/prices", json={"prices": prices}
        ).json()

    @validate_id_and_value
    def refresh_stock(self, ms_id: str, value: int):
        mapped_data = self._collector_service.get_mapped_data([ms_id])
        offer_id = mapped_data[0].offer_id
        resp = self._session.post(
            f"{settings.ozon_api_url}v1/product/import/stocks",
            json={"stocks": [{"offer_id": offer_id, "stock": value}]},
        )
        return resp.json()

    @validate_warehouse_id
    def refresh_stock_by_warehouse(self, ms_id: str, value: int, warehouse_id: int):
        mapped_data = self._collector_service.get_mapped_data([ms_id])
        offer_id = mapped_data[0].offer_id
        resp = self._session.post(
            f"{settings.ozon_api_url}v2/products/stocks",
            json={
                "stocks": [
                    {"offer_id": offer_id, "stock": value, "warehouse_id": warehouse_id}
                ]
            },
        )
        return resp.json()

    @validate_ids_and_values
    def refresh_stocks(self, ms_ids: List[str], values: List[int]):
        mapped_data = self._collector_service.get_mapped_data(ms_ids)
        ids_map = {item.ms_id: item.offer_id for item in mapped_data}
        if len(ms_ids) > settings.OZON_STOCK_LIMIT:
            chunks_ids, chunks_values = get_chunks(
                ms_ids, values, settings.OZON_STOCK_LIMIT
            )
            for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                self.refresh_stocks(chunk_ids, chunk_values)

        stocks = []
        for ms_id, value in zip(ms_ids, values):
            stocks.append({"offer_id": ids_map[ms_id], "stock": value})
        return self._session.post(
            f"{settings.ozon_api_url}v1/product/import/stocks", json={"stocks": stocks}
        ).json()

    @validate_warehouse_ids
    def refresh_stocks_by_warehouse(
        self, ms_ids: List[str], values: List[int], warehouse_ids: List[int]
    ):
        mapped_data = self._collector_service.get_mapped_data(ms_ids)
        ids_map = {item.ms_id: item.offer_id for item in mapped_data}
        stocks = []
        for ms_id, value, warehouse in zip(ms_ids, values, warehouse_ids):
            stocks.append(
                {"offer_id": ids_map[ms_id], "stock": value, "warehouse_id": warehouse}
            )
        return self._session.post(
            f"{settings.ozon_api_url}v2/products/stocks", json={"stocks": stocks}
        ).json()

    def refresh_status(self, wb_order_id, status):
        raise NotImplementedError

    def refresh_statuses(self, wb_order_ids, statuses):
        raise NotImplementedError
