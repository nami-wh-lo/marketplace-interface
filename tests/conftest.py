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
        f"{settings.wb_api_url}public/api/v1/info",
        json=[
            {"nmId": 1231312, "price": 10, "discount": 10, "promoCode": 5},
            {"nmId": 1323312, "price": 20, "discount": 10, "promoCode": 5},
        ],
    )
    mock_api.post(
        f"{settings.wb_api_url}public/api/v1/prices",
        status_code=200,
        json={"uploadId": 612455},
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
