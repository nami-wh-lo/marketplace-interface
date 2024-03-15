class Settings:
    wb_api_url: str = "https://suppliers-api.wildberries.ru/"
    wb_price_url: str = "https://discounts-prices-api.wb.ru/"
    ozon_api_url: str = "https://api-seller.ozon.ru/"
    WB_ITEMS_REFRESH_LIMIT: int = 1000
    MAPPING_LIMIT: int = 100
    OZON_STOCK_LIMIT: int = 100
    OZONE_PRICE_LIMIT: int = 1000


settings = Settings()
