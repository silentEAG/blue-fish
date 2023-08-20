
from bs4 import BeautifulSoup

from crawler.tttang import TTTangCrawler
from sync import BaseSync
from settings import config
from log import logger
from task import HttpTask
from sync import Index, Storage

class TTTangSync(BaseSync):

    def __init__(self):
        super().__init__(baseurl="https://tttang.com", index_name="tttang")
        self.crawler = TTTangCrawler

    def parse_page(self, text) -> Storage:

        soup = BeautifulSoup(text, 'html.parser')

        archives = soup.find_all("div", class_="media media-list px-md-4 px-2")

        idxs = []

        for archive in archives:

            title = archive.find("a", class_="title").text.strip()
            url = archive.find("a", class_="title")["href"].strip()
            time = archive.find("span", class_="time").text.strip()

            flag = url.split("/")[-2]

            idx = Index(title, self.baseurl + url, time, flag)
            idxs.append(idx)
        
        logger.debug("Parsed {} idxs".format(len(idxs)))
        
        return idxs
    
    def get_fully_storage(self):
        logger.info("Get fully index to sync '{}'".format(self.index_name))
        
        total_page = self.get_total_page()
        page_urls = [self.baseurl + "/?page={}".format(x) for x in range(1, total_page + 1)]
        
        get_idx_task = HttpTask(page_urls, self.parse_page_async)
        results = get_idx_task.run_with_blocking()

        flat_results = [item for sublist in results for item in sublist]
        flat_results = sorted(flat_results, key=lambda x: x.flag, reverse=True)

        logger.debug("Total idxs: {}".format(len(flat_results)))
        
        return Storage(self.index_name, flat_results)
        

    def get_remote_storage(self, last_idx = None):

        # The first time to sync or force to sync
        if last_idx is None or config.force:
            return self.get_fully_storage()

        for page in range(1, self.get_total_page() + 1):

            url = self.baseurl + "/?page={}".format(page)
            text = HttpTask.simple_request(url).decode()

            storage = Storage(self.index_name, self.parse_page(text))
            idxs = []
            for idx in storage.idxs:
                if idx == last_idx:
                    return Storage(self.index_name, idxs)
                
                idxs.append(idx)
                
        
    def get_total_page(self) -> int:
        text = HttpTask.simple_request(self.baseurl).decode()

        soup = BeautifulSoup(text, 'html.parser')
        total_page = int(soup.find_all("a", class_="page-link")[-1]["href"].split("=")[-1])

        return total_page