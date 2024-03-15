import pytest
from pydantic import ValidationError

from marketpalce_handler.schemas import CollectorItem


class TestOzon:
    def test_collector(self, ozon, collector):
        result = ozon._collector_service.get_mapped_data(["1", "2"])
        assert len(result) == 2
        assert (
            CollectorItem(
                ms_id="1", product_id="125", offer_id="123", price=10, sku="123"
            )
            in result
        )
        assert (
            CollectorItem(
                ms_id="2", product_id="126", offer_id="124", price=20, sku="124"
            )
            in result
        )

    def test_refresh_price(self, ozon, collector, ozon_prices):
        assert ozon.refresh_price("1", 100)

    @pytest.mark.parametrize(
        "ms_id, value",
        [
            ("1", "0"),
            (2, 2),
        ],
    )
    def test_refresh_price_with_invalid_parameters(
        self, ozon, collector, ozon_prices, ms_id, value
    ):
        with pytest.raises(AssertionError):
            ozon.refresh_price(ms_id, value)

    def test_refresh_prices(self, ozon, collector, ozon_prices):
        assert ozon.refresh_prices(["1", "2"], [100, 200])

    @pytest.mark.parametrize(
        "ms_ids, values",
        [
            (["1", 2], [200, 300]),
            (["1", "2"], ["str", 300]),
        ],
    )
    def test_refresh_prices_with_invalid_parameters(
        self, ozon, collector, ozon_prices, ms_ids, values
    ):
        with pytest.raises(ValidationError):
            ozon.refresh_prices(ms_ids, values)

    def test_refresh_prices_with_invalid_length(self, ozon, collector, ozon_prices):
        with pytest.raises(AssertionError):
            ozon.refresh_prices(["1", "2"], [100, 200, 300])

    def test_refresh_stock(self, ozon, collector, ozon_stocks):
        assert ozon.refresh_stock("1", 100)

    def test_refresh_stock_by_warehouse(self, ozon, collector, ozon_stocks):
        assert ozon.refresh_stock_by_warehouse("1", 100, 1)

    @pytest.mark.parametrize(
        "ms_id, value",
        [
            ("1", "0"),
            (2, 2),
        ],
    )
    def test_refresh_stock_with_invalid_parameters(
        self, ozon, collector, ozon_stocks, ms_id, value
    ):
        with pytest.raises(AssertionError):
            ozon.refresh_stock(ms_id, value)

    @pytest.mark.parametrize(
        "ms_id, value, warehouse_id",
        [
            ("1", "s0", 1),
            (2, 2, 1),
        ],
    )
    def test_refresh_stock_by_warehouse_with_invalid_parameters(
        self, ozon, collector, ozon_stocks, ms_id, value, warehouse_id
    ):
        with pytest.raises(AssertionError):
            ozon.refresh_stock_by_warehouse(ms_id, value, warehouse_id)

    def test_refresh_stocks(self, ozon, collector, ozon_stocks):
        assert ozon.refresh_stocks(["1", "2"], [1, 3])

    def test_refresh_stocks_by_warehouse(self, ozon, collector, ozon_stocks):
        assert ozon.refresh_stocks_by_warehouse(["1", "2"], [1, 3], [1, 2])

    @pytest.mark.parametrize(
        "ms_ids, values",
        [
            (["1", 2], [2, 3]),
            (["1", "2"], ["str", 3]),
        ],
    )
    def test_refresh_stocks_with_invalid_parameters(
        self, ozon, collector, ozon_stocks, ms_ids, values
    ):
        with pytest.raises(ValidationError):
            ozon.refresh_stocks(ms_ids, values)

    @pytest.mark.parametrize(
        "ms_ids, values, warehouse_ids",
        [
            (["1", 2], [2, 3], [1, 2]),
            (["1", "2"], ["str", 3], [1, 2]),
        ],
    )
    def test_refresh_stocks_by_warehouse_with_invalid_parameters(
        self, ozon, collector, ozon_stocks, ms_ids, values, warehouse_ids
    ):
        with pytest.raises(ValidationError):
            ozon.refresh_stocks_by_warehouse(ms_ids, values, warehouse_ids)

    def test_refresh_stocks_with_invalid_length(self, ozon, collector, ozon_stocks):
        with pytest.raises(AssertionError):
            ozon.refresh_stocks(["1", "2"], [1, 2, 3])

    def test_refresh_stocks_by_warehouse_with_invalid_length(
        self, ozon, collector, ozon_stocks
    ):
        with pytest.raises(AssertionError):
            ozon.refresh_stocks_by_warehouse(["1", "2"], [1, 2], [1, 2, 3])
