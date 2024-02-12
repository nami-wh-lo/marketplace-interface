from pydantic import BaseModel


class MsItem(BaseModel):
    ms_id: str
    barcodes: str
    nm_id: int
    name: str
    value: int


class WbUpdateItem(MsItem):
    current_value: int
