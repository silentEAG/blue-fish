from bs4 import BeautifulSoup

from crawler import BaseCrawler, converter
from utils import random_string
from log import logger

class XZCrawler(BaseCrawler):

    def __init__(self, name = "xz"):
        super().__init__(name)
        self.headers = {
            "Cache-Control": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "https://xz.aliyun.com/",
        }

    async def parse(self, text: str):
        """
        Parse the html to markdown
        """
        soup = BeautifulSoup(text, 'html.parser')

        title = soup.find("span", class_="content-title").text

        text = soup.find("div", class_="main-topic")
        text.find("div", class_="clearfix user-info topic-list").decompose()
        text.find("div", class_="related-section").decompose()
        text = converter.convert_soup(text)
        path = random_string()

        
        logger.info("Parsing '{}'".format(title))
        await self.save_to_file(text, title, path)
