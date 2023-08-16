import asyncio
import aiohttp
import requests
import concurrent.futures

from log import logger
from settings import config
from utils import get_random_proxy

class HttpTask:
    def __init__(self, urls: list[str], callback):
        self.urls = urls
        self.callback = callback

    def run_with_blocking(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run())

    @staticmethod
    def simple_request(url: str, additonal_headers = None):
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
        header.update(additonal_headers or {})

        response = requests.get(url, headers=header)
        if response.status_code != 200:
            logger.error("[{}] Failed to fetch with code {}".format(url, response.status_code))
            return None
        return response.content

    async def fetch(self, url, session, semaphore):
        async with semaphore:
            async with session.get(url, proxy=config.proxy) as response:
                if response.status != 200:
                    logger.error("[{}] Failed to fetch with code {}".format(url, response.status_code))
                    # response.raise_for_status()
                try:
                    data = await response.text()
                except:
                    await asyncio.sleep(1.5)
                    data = await response.text()
                return await self.callback(data)

    async def run(self):
        semaphore = asyncio.Semaphore(3)
        tasks = []
        logger.info("Fetching {} urls".format(len(self.urls)))
        async with aiohttp.ClientSession() as session:
            for url in self.urls:
                tasks.append(self.fetch(url, session, semaphore))
            res = await asyncio.gather(*tasks)
            return res