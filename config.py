import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    bgd_token: str = os.getenv("BGD_TOKEN")
    bgd_token_url: str = os.getenv("BGD_TOKEN_URL")
    wb_api_url: str = os.getenv("WB_API_URL")
    bgd_mapping_url: str = os.getenv("BGD_MAPPING_URL")

    WB_STOCK_REFRESH_LIMIT: int = 1000


settings = Settings()
