class Settings:
    wb_api_url: str = "https://suppliers-api.wildberries.ru/"
    wb_price_url: str = "https://discounts-prices-api.wb.ru/"
    WB_ITEMS_REFRESH_LIMIT: int = 1000


settings = Settings()
