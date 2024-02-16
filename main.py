import os

from marketpalce_handler import Wildberries
from dotenv import load_dotenv

load_dotenv()

serv = Wildberries(
    token_id=3,
    token_service_token="token",
    token_service_url="url",
    mapping_url="url",
)
