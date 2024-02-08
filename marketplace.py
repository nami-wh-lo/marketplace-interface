from abc import ABC, abstractmethod

from requests import HTTPError

from config import settings
import requests

from logger import get_logger


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
        self.logger = get_logger()

        headers = {
            "Authorization": f"Token {settings.bgd_token}",
        }
        response = requests.get(settings.bgd_token_url, headers=headers)
        for i in response.json():
            warehouse_id = i["warehouse_id"]
            if warehouse_id and i["id"] == token_id:
                self.warehouse_id = warehouse_id
                self.token = i["common_token"]
                self.headers = {
                    "Authorization": f"{self.token}",
                }
                self.logger.info(f"Wildberries is initialized")
                break
        if not hasattr(self, "warehouse_id"):
            self.logger.error(f"Wildberries is not initialized")
            raise Exception("Token not found")

    def get_stock(self, ms_id):
        try:
            data = get_mapped_data(ms_id)
            resp = requests.post(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "skus": [data["barcodes"]],
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            self.logger.info(f"Wildberries: {ms_id} stock is refreshed")
            return True
        except HTTPError as e:
            self.logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    def refresh_stock(self, ms_id, value):
        try:
            data = get_mapped_data(ms_id)
            resp = requests.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json=[
                    {
                        "sku": [data["barcodes"]],
                        "amount": value,
                    },
                ],
                headers=self.headers,
            )
            resp.raise_for_status()
            self.logger.info(f"Wildberries: {ms_id} stock is refreshed")
            return True
        except HTTPError as e:
            self.logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    def refresh_stocks(self, ids: list[str], values: list[int]):
        try:
            json_data = []
            for ms_id, value in zip(ids, values):
                data = get_mapped_data(ms_id)

                json_data.append(
                    {
                        "sku": [data["barcodes"]],
                        "amount": value,
                    }
                )
            resp = requests.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json=json_data,
                headers=self.headers,
            )
            resp.raise_for_status()
            self.logger.info(f"Wildberries: {ids} stock is refreshed")
            return True
        except HTTPError as e:
            self.logger.error(
                f"Wildberries: {ids} stock is not refreshed. Error: {e}"
            )
            raise e

    def get_price(self):
        resp = requests.get(
            f"{settings.wb_api_url}public/api/v1/info", headers=self.headers
        )
        return True

    def refresh_price(self, ms_id, value):
        try:
            data = get_mapped_data(ms_id)

            json_data = [
                {
                    "nmId": int(data["nm_id"]),
                    "price": value,
                },
            ]

            resp = requests.post(
                f"{settings.wb_api_url}public/api/v1/prices",
                headers=self.headers,
                json=json_data,
            )
            resp.raise_for_status()
            self.logger.info(f"Wildberries: {ms_id} price is refreshed")
            return True
        except HTTPError as e:
            self.logger.error(
                f"Wildberries: {ms_id} price is not refreshed. Error: {e}"
            )
            raise e

    def refresh_prices(self, ids: list[int], values: list[int]):
        json_data = []
        for ms_id, value in zip(ids, values):
            data = get_mapped_data(ms_id)

            json_data.append(
                {
                    "nmId": int(data["nm_id"]),
                    "price": value,
                }
            )

        resp = requests.post(
            f"{settings.wb_api_url}public/api/v1/prices",
            headers=self.headers,
            json=json_data,
        )
        print(resp.status_code)
        print(resp.json())
        return True

    def refresh_status(self, ms_id, value):
        print(f"Wildberries: {ms_id} status is {value}")

    def refresh_statuses(self, ids: list[str], values: list[int]):
        for i in range(len(ids)):
            self.refresh_status(ids[i], values[i])


def get_mapped_data(ms_id):
    resp = requests.get(f"{settings.bgd_mapping_url}", params={"ms_id": ms_id})
    return resp.json()[0]

