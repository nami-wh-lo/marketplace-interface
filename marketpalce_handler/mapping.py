from typing import List

from requests import Session

from marketpalce_handler.schemas import MsItem
from marketpalce_handler.validators import validate_ids_and_values


class Mapping:

    def __init__(self, mapping_url: str, session: Session):
        self.session = session
        self.mapping_url = mapping_url

    @validate_ids_and_values
    def get_mapped_data(self, ms_ids: List[str], values: List[int]) -> List[MsItem]:
        ms_items = self.session.get(
            f"{self.mapping_url}", params={"ms_id": ",".join(ms_ids)}
        )
        if len(ms_ids) == 1:
            return [MsItem(**ms_items.json()[0], value=values[0])]
        id_value_map = dict(zip(ms_ids, values))
        mapped_data = []

        for item in ms_items.json():
            value = id_value_map.get(item["ms_id"])
            item["value"] = value
            mapped_data.append(MsItem(**item))

        return mapped_data
