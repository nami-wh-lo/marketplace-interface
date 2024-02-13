import os

from marketpalce_handler import Wildberries
from dotenv import load_dotenv

load_dotenv()

serv = Wildberries(
    token_id=3,
    bgd_token=os.getenv("BGD_TOKEN"),
    bgd_token_url=os.getenv("BGD_TOKEN_URL"),
    bgd_mapping_url=os.getenv("BGD_MAPPING_URL"),
)
