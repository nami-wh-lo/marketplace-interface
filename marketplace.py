from abc import ABC, abstractmethod
from typing import List, Union

from requests import HTTPError

from config import settings
import requests

from logger import get_logger
from models import MsItem, WbUpdateItem


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
    def refresh_statuses(self, ids: list[int], values: list[int]):
        pass


class Wildberries(Marketplace):
    def __init__(self, token_id):
        self._logger = get_logger()
        self._session = requests.Session()
        headers = {
            "Authorization": f"Token {settings.bgd_token}",
        }
        response = self._session.get(settings.bgd_token_url, headers=headers)
        for i in response.json():
            warehouse_id = i["warehouse_id"]
            if warehouse_id and i["id"] == token_id:
                self.warehouse_id = warehouse_id
                self.token = i["common_token"]
                self.headers = {
                    "Authorization": f"{self.token}",
                }
                self._logger.debug("Wildberries is initialized")
                break
        if not hasattr(self, "warehouse_id"):
            self._logger.error("Warehouse id is not found")
            raise Exception("Warehouse id is not found")

    def get_stock(self, ms_id):
        try:
            data = self.get_mapped_data(ms_id, 0)
            resp = self._session.post(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "skus": [data[0].barcodes],
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            self._logger.info(f"Wildberries: {ms_id} stock is refreshed")
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    def refresh_stock(self, ms_id, value):
        try:
            data = self.get_mapped_data(ms_id, value)
            resp = self._session.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "stocks": [
                        {
                            "sku": data[0].barcodes,
                            "amount": value,
                        },
                    ]
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            self._logger.info(f"Wildberries: {ms_id} stock is refreshed")
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    def refresh_stocks(self, ids: list[str], values: list[int]):
        try:
            json_data = []
            if len(ids) != len(values):
                raise ValueError("ids and values should have the same length")

            if len(ids) > settings.WB_ITEMS_REFRESH_LIMIT:
                chunks_ids, chunks_values = self.get_chunks(ids, values)
                for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                    self.refresh_stocks(chunk_ids, chunk_values)

            for item in self.get_mapped_data(ids, values):
                json_data.append(
                    {
                        "sku": item.barcodes,
                        "amount": item.value,
                    }
                )
            resp = self._session.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "stocks": json_data,
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return True
        except HTTPError as e:
            self._logger.error(f"Wildberries: {ids} stock is not refreshed. Error: {e}")
            raise e

    def get_price(self):
        resp = self._session.get(
            f"{settings.wb_api_url}public/api/v1/info", headers=self.headers
        )
        return {price["nmId"]: price["price"] for price in resp.json()}

    def refresh_price(self, ms_id, value):
        try:
            data = self.get_mapped_data(ms_id, value)[0]

            initial_price = self.get_price().get(data.nm_id)

            return self._update_prices(
                [
                    WbUpdateItem(
                        **data.dict(),
                        current_value=initial_price,
                    )
                ]
            )
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} price is not refreshed. Error: {e}"
            )
            raise e

    def refresh_prices(self, ids: list[str], values: list[int]):
        if len(ids) != len(values):
            raise ValueError("ids and values should have the same length")

        if len(ids) > settings.WB_ITEMS_REFRESH_LIMIT:
            chunks_ids, chunks_values = self.get_chunks(ids, values)
            for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                self.refresh_price(chunk_ids, chunk_values)

        initial_prices = self.get_price()
        items_to_reprice = []
        for item in self.get_mapped_data(ids, values):
            items_to_reprice.append(
                WbUpdateItem(
                    **item.dict(),
                    current_value=initial_prices.get(item.nm_id),
                )
            )

        return self._update_prices(items_to_reprice)

    def _update_prices(self, items: List[WbUpdateItem]):
        items_to_reprice: List[WbUpdateItem] = []
        json_data = []
        for item in items:
            if item.current_value * 2 < item.value:
                json_data.append(
                    {
                        {
                            "nmId": item.nm_id,
                            "price": item.current_value * 2,
                        },
                    }
                )
                items_to_reprice.append(
                    WbUpdateItem(
                        ms_id=item.ms_id,
                        barcodes=item.barcodes,
                        nm_id=item.nm_id,
                        name=item.name,
                        value=item.value,
                        current_value=item.current_value * 2,
                    )
                )
            else:
                json_data.append(
                    {
                        {
                            "nmId": item.nm_id,
                            "price": item.value,
                        },
                    }
                )
        resp = requests.post(
            f"{settings.wb_api_url}public/api/v1/prices",
            headers=self.headers,
            json=json_data,
        )
        self._logger.info(f"response: {resp.status_code} {resp.json()}")
        resp.raise_for_status()
        if items_to_reprice:
            self._update_prices(items_to_reprice)
        return resp.json()

    def refresh_status(self, ms_id, value):
        print(f"Wildberries: {ms_id} status is {value}")

    def refresh_statuses(self, ids: list[str], values: list[int]):
        for i in range(len(ids)):
            self.refresh_status(ids[i], values[i])

    @staticmethod
    def get_mapped_data(
        ms_ids: Union[str, List[str]], values: Union[int, List[int]]
    ) -> List[MsItem]:
        resp = requests.get(
            f"{settings.bgd_mapping_url}", params={"ms_id": ",".join(ms_ids)}
        )

        if isinstance(ms_ids, str):
            print("str")
            return [MsItem(**resp.json()[0], value=values)]

        id_value_map = dict(zip(ms_ids, values))

        mapped_data = []
        for item in resp.json():
            value = id_value_map.get(item["ms_id"])
            item["value"] = value
            mapped_data.append(MsItem(**item))
        return mapped_data

    @staticmethod
    def get_chunks(ids, values):
        chunks_ids = [
            ids[i : i + settings.WB_ITEMS_REFRESH_LIMIT]
            for i in range(0, len(ids), settings.WB_ITEMS_REFRESH_LIMIT)
        ]
        chunks_values = [
            values[i : i + settings.WB_ITEMS_REFRESH_LIMIT]
            for i in range(0, len(values), settings.WB_ITEMS_REFRESH_LIMIT)
        ]
        return chunks_ids, chunks_values
