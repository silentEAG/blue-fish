from bs4 import BeautifulSoup

from sync import BaseSync
from settings import config
from log import logger
from task import HttpTask
from sync import Index, Storage
import re


date = re.compile(r"\d{4}-\d{2}-\d{2}")

class XZSync(BaseSync):

    def __init__(self):
        super().__init__(baseurl="https://xz.aliyun.com", index_name="xz")


    def parse_page(self, text):

        soup = BeautifulSoup(text, 'html.parser')

        archives = soup.find_all("td")

        idxs = []

        for archive in archives:
            
            title = archive.find("a", class_="topic-title").text.strip()
            url = archive.find("a", class_="topic-title")["href"].strip()
            time = archive.find("p", class_="topic-info").text.strip()
            time = date.search(time).group(0)

            flag = url.split("/")[-1]

            idx = Index(title, self.baseurl + url, time, flag)
            idxs.append(idx)
        
        logger.debug("Parsed {} idxs".format(len(idxs)))
        
        return idxs
    
    def get_fully_storage(self):
        logger.info("Get fully index to sync '{}'".format(self.index_name))
        
        total_page = self.get_total_page()
        page_urls = [self.baseurl + "/?page={}".format(x) for x in range(1, 1 + 1)]
        
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

            sources = self.parse_page(text)
            idxs = []
            for idx in sources:
                if idx == last_idx:
                    return Storage(self.index_name, idxs)
                
                idxs.append(idx)
        

    def get_total_page(self) -> int:
        text = HttpTask.simple_request(self.baseurl).decode()

        soup = BeautifulSoup(text, 'html.parser')
        total_page = int(soup.find_all("a", class_="active")[-1].text.split("/")[-1])

        return total_page