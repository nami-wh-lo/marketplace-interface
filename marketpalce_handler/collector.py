import asyncio
from .schemas import CollectorItem
import aiohttp


class Collector:
    def __init__(self, collector_api_key: str, collector_url: str):
        self.collector_api_key = collector_api_key
        self.collector_url = collector_url

    def get_mapped_data(self, ms_ids):
        mapped_data = asyncio.run(self.fetch_mapped_data(ms_ids))
        return [
            CollectorItem(
                ms_id=item.get("ms_id"),
                product_id=item.get("ozon_product_id"),
                offer_id=item.get("code"),
                price=round(item.get("ozon_max_price") / 100, 2),
                sku=item["attributes"]["79c718d6-8526-11ee-0a80-065e00096935"]["value"],
            )
            for item in mapped_data
        ]

    async def fetch_mapped_data(self, ms_ids):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for i in ms_ids:
                url = f"{self.collector_url}/v1/products/additional/cmd?ms_id={i}"
                headers = {"Authorization": self.collector_api_key}
                task = asyncio.create_task(self.fetch_item(session, url, headers))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            return responses

    @staticmethod
    async def fetch_item(session, url, headers):
        async with session.get(url, headers=headers) as response:
            return await response.json()
