import re

import pytest
import requests_mock

from marketpalce_handler import Wildberries
from marketpalce_handler.config import settings


@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mapping(mock_api):
    mock_api.get(
        "https://mapping_url",
        json=[
            {
                "ms_id": "1",
                "barcodes": "12313",
                "nm_id": 1231312,
                "name": "some_name",
            },
            {
                "ms_id": "2",
                "barcodes": "22313",
                "nm_id": 1323312,
                "name": "another_name",
            },
        ],
    )


@pytest.fixture
def prices(mock_api):
    mock_api.get(
        f"{settings.wb_price_url}api/v2/list/goods/filter",
        json={
            "data": {
                "listGoods": [
                    {
                        "nmID": 1231312,
                        "vendorCode": "07326060",
                        "sizes": [
                            {
                                "sizeID": 3123515574,
                                "price": 10,
                                "discountedPrice": 9,
                                "techSizeName": 42,
                            }
                        ],
                        "currencyIsoCode4217": "RUB",
                        "discount": 10,
                        "editableSizePrice": True,
                    },
                    {
                        "nmID": 1323312,
                        "vendorCode": "0767656",
                        "sizes": [
                            {
                                "sizeID": 3123515574,
                                "price": 20,
                                "discountedPrice": 18,
                                "techSizeName": 42,
                            }
                        ],
                        "currencyIsoCode4217": "RUB",
                        "discount": 10,
                        "editableSizePrice": True,
                    },
                ]
            }
        },
    )
    mock_api.post(
        f"{settings.wb_price_url}api/v2/upload/task",
        status_code=200,
        json={
            "data": {"id": 612455, "alreadyExists": False},
            "error": False,
            "errorText": "",
        },
    )


@pytest.fixture
def statuses(mock_api):
    mock_api.post(f"{settings.wb_api_url}api/v3/supplies", json={"id": "WB-GI-1234567"})
    cancel_order_url_matcher = re.compile(
        f"{settings.wb_api_url}api/v3/orders/\d+/cancel"
    )
    mock_api.patch(
        cancel_order_url_matcher,
        status_code=204,
    )

    add_order_url_matcher = re.compile(
        f"{settings.wb_api_url}api/v3/supplies/WB-GI-1234567/orders/\d+"
    )
    mock_api.patch(
        add_order_url_matcher,
        status_code=204,
    )


@pytest.fixture
def wildberries(mock_api, mapping):
    mock_api.get(
        "https://token_service_url",
        json=[{"warehouse_id": 123, "id": 1, "common_token": "token"}],
    )
    return Wildberries(
        token_id=1,
        token_service_token="token",
        token_service_url="https://token_service_url",
        mapping_url="https://mapping_url",
    )
