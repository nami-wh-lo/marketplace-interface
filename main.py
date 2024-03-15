from marketpalce_handler import Wildberries, Ozon
from dotenv import load_dotenv

load_dotenv()

wb = Wildberries(
    token_id=3,
    token_service_token="token",
    token_service_url="token_service_url",
    mapping_url="mapping_url",
)


ozon = Ozon(
    client_id="client_id",
    api_key="api_key",
    collector_api_key="collector_api_key",
    collector_url="https://collector_url",
)
