from typing import List, Dict

from requests import HTTPError

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .exceptions import InitialisationException, InvalidStatusException
from .logger import get_logger
from .config import settings
from .mapping import Mapping
from .marketplace import Marketplace
from .schemas import WbUpdateItem
from .validators import (
    validate_ids_and_values,
    validate_id_and_value,
    validate_statuses,
)


class Wildberries(Marketplace):
    def __init__(
        self,
        token_id,
        token_service_token,
        token_service_url,
        mapping_url,
        max_price_requests: int = 5,
        session: requests.Session = requests.Session(),
    ):
        self._logger = get_logger()
        self._session = session
        self._mapping_service = Mapping(mapping_url, self._session)
        self._max_price_requests = max_price_requests
        retries = Retry(
            total=3,
            backoff_factor=0.5,
        )
        self._session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            tokens = self._session.get(
                token_service_url,
                headers={
                    "Authorization": f"Token {token_service_token}",
                },
                timeout=5,
            )
            tokens.raise_for_status()
            for token in tokens.json():
                warehouse_id = token.get("warehouse_id")
                if warehouse_id and token.get("id") == token_id:
                    self.warehouse_id = warehouse_id
                    self._session.headers.update(
                        {
                            "Authorization": f"{token['common_token']}",
                        }
                    )
                    self._logger.debug("Wildberries is initialized")
                    break
        except HTTPError:
            self._logger.error("Can't connect to token service")
            raise InitialisationException(
                f"Can't connect to token service {tokens.status_code}"
            )

        if not hasattr(self, "warehouse_id"):
            self._logger.error("Warehouse id is not found")
            raise InitialisationException("Warehouse id is not found")

    def get_stock(self, ms_id: str):
        try:
            assert isinstance(ms_id, str)
            ms_items = self._mapping_service.get_mapped_data([ms_id], [0])[0]
            stocks = self._session.post(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "skus": [ms_items.barcodes],
                },
                timeout=5,
            )
            stocks.raise_for_status()
            return stocks.json()
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    @validate_id_and_value
    def refresh_stock(self, ms_id: str, value: int):
        try:
            ms_items = self._mapping_service.get_mapped_data([ms_id], [value])[0]
            refresh_stock_resp = self._session.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "stocks": [
                        {
                            "sku": ms_items.barcodes,
                            "amount": value,
                        },
                    ]
                },
                timeout=5,
            )
            refresh_stock_resp.raise_for_status()
            self._logger.info(f"Wildberries: {ms_id} stock is refreshed")
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} stock is not refreshed. Error: {e}"
            )
            raise e

    @validate_ids_and_values
    def refresh_stocks(self, ms_ids: List[str], values: List[int]):
        try:
            json_data = []
            if len(ms_ids) > settings.WB_ITEMS_REFRESH_LIMIT:
                chunks_ids, chunks_values = self.get_chunks(ms_ids, values)
                for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                    self.refresh_stocks(chunk_ids, chunk_values)

            for item in self._mapping_service.get_mapped_data(ms_ids, values):
                json_data.append(
                    {
                        "sku": item.barcodes,
                        "amount": item.value,
                    }
                )
            refresh_stocks_resp = self._session.put(
                f"{settings.wb_api_url}api/v3/stocks/{self.warehouse_id}",
                json={
                    "stocks": json_data,
                },
                timeout=5,
            )
            refresh_stocks_resp.raise_for_status()
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_ids} stock is not refreshed. Error: {e}"
            )
            raise e

    def get_price(self) -> Dict:
        products = dict()
        for i in range(0, self._max_price_requests + 1):
            try:
                prices = self._session.get(
                    f"{settings.wb_price_url}api/v2/list/goods/filter",
                    timeout=5,
                    params={
                        "limit": settings.WB_ITEMS_REFRESH_LIMIT,
                        "offset": i * settings.WB_ITEMS_REFRESH_LIMIT,
                    },
                )
                if prices:
                    products.update(
                        {
                            product["nmID"]: {
                                "price": product["sizes"][0]["price"],
                                "discount": product["discount"],
                            }
                            for product in prices.json()["data"]["listGoods"]
                        }
                    )
                if (
                    len(prices.json()["data"]["listGoods"])
                    < settings.WB_ITEMS_REFRESH_LIMIT
                ):
                    break
            except HTTPError as e:
                self._logger.error(f"Wildberries: prices are not refreshed. Error: {e}")
                raise e
        return products

    @validate_id_and_value
    def refresh_price(self, ms_id: str, value: int):
        try:
            ms_items = self._mapping_service.get_mapped_data([ms_id], [value])[0]

            initial_price = self.get_price().get(ms_items.nm_id)["price"]

            self._update_prices(
                [
                    WbUpdateItem(
                        **ms_items.dict(),
                        current_value=initial_price,
                    )
                ],
                "price",
            )
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} price is not refreshed. Error: {e}"
            )
            raise e

    @validate_ids_and_values
    def refresh_prices(self, ms_ids: List[str], values: List[int]):
        if len(ms_ids) > settings.WB_ITEMS_REFRESH_LIMIT:
            chunks_ids, chunks_values = self.get_chunks(ms_ids, values)
            for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                self.refresh_price(chunk_ids, chunk_values)

        initial_prices = self.get_price()
        items_to_reprice = []
        for item in self._mapping_service.get_mapped_data(ms_ids, values):
            items_to_reprice.append(
                WbUpdateItem(
                    **item.dict(),
                    current_value=initial_prices.get(item.nm_id)["price"],
                )
            )

        self._update_prices(items_to_reprice, "price")
        return True

    @validate_id_and_value
    def refresh_discount(self, ms_id: str, value: int):
        try:
            ms_items = self._mapping_service.get_mapped_data([ms_id], [value])[0]

            initial_price = self.get_price().get(ms_items.nm_id)["discount"]

            self._update_prices(
                [
                    WbUpdateItem(
                        **ms_items.dict(),
                        current_value=initial_price,
                    )
                ],
                "discount",
            )
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {ms_id} price is not refreshed. Error: {e}"
            )
            raise e

    @validate_ids_and_values
    def refresh_discounts(self, ms_ids: List[str], values: List[int]):
        if len(ms_ids) > settings.WB_ITEMS_REFRESH_LIMIT:
            chunks_ids, chunks_values = self.get_chunks(ms_ids, values)
            for chunk_ids, chunk_values in zip(chunks_ids, chunks_values):
                self.refresh_price(chunk_ids, chunk_values)

        initial_prices = self.get_price()
        items_to_reprice = []
        for item in self._mapping_service.get_mapped_data(ms_ids, values):
            items_to_reprice.append(
                WbUpdateItem(
                    **item.dict(),
                    current_value=initial_prices.get(item.nm_id)["discount"],
                )
            )

        self._update_prices(items_to_reprice, "discount")
        return True

    def _update_prices(self, items: List[WbUpdateItem], update_value):
        items_to_reprice: List[WbUpdateItem] = []
        json_data = []
        for item in items:
            if item.current_value * 2 < item.value:
                json_data.append(
                    {
                        "nmId": item.nm_id,
                        update_value: item.current_value * 2,
                    },
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
                        "nmId": item.nm_id,
                        update_value: item.value,
                    },
                )
        try:
            price_update_resp = self._session.post(
                f"{settings.wb_price_url}api/v2/upload/task",
                json={"data": json_data},
                timeout=5,
            )
            price_update_resp.raise_for_status()
            self._logger.info(
                f"response: {price_update_resp.status_code} {price_update_resp.json()}"
            )
        except HTTPError as e:
            self._logger.error(f"Wildberries: prices are not refreshed. Error: {e}")
            raise e
        if items_to_reprice:
            self._update_prices(items_to_reprice, "price")
        return True

    def refresh_status(self, wb_order_id: int, status_name: str, supply_id: str = None):
        assert isinstance(wb_order_id, int)
        assert isinstance(status_name, str)
        try:
            match status_name:
                case "confirm":
                    supply_id = supply_id or self._session.post(
                        f"{settings.wb_api_url}api/v3/supplies",
                        json={"name": f"supply_order{wb_order_id}"},
                        timeout=5,
                    ).json().get("id")
                    add_order_to_supply_resp = requests.patch(
                        f"{settings.wb_api_url}api/v3/supplies/{supply_id}/orders/{wb_order_id}",
                    )
                    add_order_to_supply_resp.raise_for_status()
                case "cancel":
                    cancel_order_resp = requests.patch(
                        f"{settings.wb_api_url}api/v3/orders/{wb_order_id}/cancel"
                    )
                    cancel_order_resp.raise_for_status()
                case _:
                    raise InvalidStatusException(
                        f"{status_name} is not valid status name"
                    )
            return True
        except HTTPError as e:
            self._logger.error(
                f"Wildberries: {wb_order_id} status is not refreshed. Error: {e}"
            )
            raise e

    @validate_statuses
    def refresh_statuses(self, wb_order_ids: List[int], statuses: List[str]):
        try:
            new_supply = self._session.post(
                f"{settings.wb_api_url}api/v3/supplies",
                json={"name": "supply_orders"},
                timeout=5,
            ).json()

            for wb_order_id, status in zip(wb_order_ids, statuses):
                self.refresh_status(
                    wb_order_id=wb_order_id,
                    status_name=status,
                    supply_id=new_supply.get("id"),
                )
            return True
        except HTTPError as e:
            self._logger.error(f"Wildberries: can't create new supply. Error: {e}")
            raise e

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
