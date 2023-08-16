from bs4 import BeautifulSoup

from crawler import BaseCrawler, converter
from utils import random_string
from log import logger

class TTTangCrawler(BaseCrawler):

    def __init__(self, name = "tttang"):
        super().__init__(name)
    

    async def parse(self, text: str):
        """
        Parse the html to markdown
        """
        soup = BeautifulSoup(text, 'html.parser')
        
        title = soup.find("h2", class_="mb-3").text
        text = soup.find("div", class_="card-content")
        text = converter.convert_soup(text)
        path = random_string()

        logger.info("Parsing '{}'".format(title))
        await self.save_to_file(text, title, path)
