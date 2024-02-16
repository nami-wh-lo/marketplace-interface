from functools import wraps
from typing import List
from .schemas import IdsValuesSchema, StatusesSchema


def validate_ids_and_values(func):
    @wraps(func)
    def wrapper(self, ms_ids: List[str], values: List[int]):
        assert len(ms_ids) == len(values)
        IdsValuesSchema(ms_ids=ms_ids, values=values)

        return func(self, ms_ids, values)

    return wrapper


def validate_id_and_value(func):
    @wraps(func)
    def wrapper(self, ms_id: str, value: int):
        assert isinstance(ms_id, str)
        assert isinstance(value, int)

        return func(self, ms_id, value)

    return wrapper


def validate_statuses(func):
    @wraps(func)
    def wrapper(self, wb_order_ids: List[int], statuses: List[str]):
        assert len(wb_order_ids) == len(statuses)
        StatusesSchema(wb_order_ids=wb_order_ids, statuses=statuses)

        return func(self, wb_order_ids, statuses)

    return wrapper
