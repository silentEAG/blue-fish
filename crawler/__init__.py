import markdownify
import re
import os
import ssl
import asyncio
import aiohttp
import hashlib

from settings import config
from task import HttpTask
from log import logger
from utils import get_random_proxy

img_regex = re.compile(r"!\[[^\]]*\]\((.*?)(#.*?)?\)")
converter = markdownify.MarkdownConverter()



class BaseCrawler(object):
    """
    Base class for all crawlers
    """
    def __init__(self, name: str):
        self.name = name
        self.headers = None

    async def parse(self, text):
        """
        Parse the text to get the idxs
        """
        pass

    def run(self, urls: list[str]):
        
        save_task = HttpTask(urls, self.parse)
        save_task.run_with_blocking()


    async def download_img(self, img_url: str, rng_path: str, session: aiohttp.ClientSession):
        """
        Download the img to local
        """
        try:
            async with session.get(img_url, headers=self.headers, proxy=config.proxy) as resp:
                img_path = os.path.join(config.save_path + config.dist_dir, self.name, "pic", rng_path, safe_filename(os.path.basename(img_url)))
                with open(img_path, 'wb') as f:
                    f.write(await resp.content.read())
        except Exception as e:
            logger.error("Failed to download img '{}' cause {}".format(img_url, e))

    async def save_to_file(self, text: str, title: str):
        """
        Save the markdown text to file
        """
        rng_path = hashlib.sha256(title.encode()).hexdigest()[:24]
        os.makedirs(os.path.join(config.save_path + config.dist_dir, self.name, "pic", rng_path), exist_ok=True)
        img_urls = [i[0] for i in img_regex.findall(text)]

        # ignore ssl error
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=ssl_context)) as session:
            tasks = [asyncio.create_task(self.download_img(img_url, rng_path, session)) for img_url in img_urls]
            if len(tasks) > 0:
                await asyncio.wait(tasks)

        def repl(match):
            img_url = match.group(1)
            img_path = os.path.join("pic", rng_path, safe_filename(os.path.basename(img_url)))
            return f"![]({img_path})"
        
        text = img_regex.sub(repl, text)
        

        with open(os.path.join(config.save_path + config.dist_dir, self.name, safe_filename(title) + ".md"), 'w', encoding="utf-8") as f:
            f.write(text)
        logger.debug("Saved '{}'".format(title))


safe_filename_regex = re.compile(r"[\/\\\:\*\?\"\<\>\|]")
def safe_filename(filename):
    return safe_filename_regex.sub("_", filename)