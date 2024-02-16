from functools import wraps
from typing import List

from pydantic import BaseModel, ValidationError, constr


class InputData(BaseModel):
    ms_ids: List[constr(strip_whitespace=True, min_length=1)]
    values: List[int]


def validate_ids_and_values(func):
    @wraps(func)
    def wrapper(self, ms_ids: List[str], values: List[int]):
        try:
            assert len(ms_ids) == len(values)
            InputData(ms_ids=ms_ids, values=values)
        except ValidationError as e:
            raise ValueError(f"Invalid input data: {e}")

        return func(self, ms_ids, values)

    return wrapper

def validate_id_and_value(func):
    @wraps(func)
    def wrapper(self, ms_id: str, value: int):
        assert isinstance(ms_id, str)
        assert isinstance(value, int)

        return func(self, ms_id, value)

    return wrapper
