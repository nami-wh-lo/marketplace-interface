import os

from marketpalce_handler import Wildberries
from dotenv import load_dotenv

load_dotenv()

serv = Wildberries(
    token_id=3,
    token=os.getenv("BGD_TOKEN"),
    token_service_url=os.getenv("BGD_TOKEN_URL"),
    mapping_url=os.getenv("BGD_MAPPING_URL"),
)

