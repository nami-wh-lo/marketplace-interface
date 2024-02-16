from typing import List

from pydantic import BaseModel, constr


class MsItem(BaseModel):
    ms_id: str
    barcodes: str
    nm_id: int
    name: str
    value: int


class WbUpdateItem(MsItem):
    current_value: int


class IdsValuesSchema(BaseModel):
    ms_ids: List[constr(strip_whitespace=True, min_length=1)]
    values: List[int]


class StatusesSchema(BaseModel):
    wb_order_ids: List[int]
    statuses: List[constr(strip_whitespace=True, min_length=1)]
