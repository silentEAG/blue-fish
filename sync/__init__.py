import json
import os

from log import logger
from settings import config
from utils import sure
from crawler.tttang import TTTangCrawler
from crawler.xz import XZCrawler

"""
crawler dict
"""
crawler = {
    "tttang": TTTangCrawler,
    "xz": XZCrawler,
}

class Index(object):
    def __init__(self, title, url, time, flag):
        self.title = title
        self.url = url
        self.time = time
        self.flag = flag
    
    def __eq__(self, other: object) -> bool:
        return self.flag == other.flag
    
    def __hash__(self) -> int:
        return hash(self.flag)
    

class StorageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Storage):
            return {"idx_name": obj.idx_name, "idxs": obj.idxs}
        if isinstance(obj, Index):
            return {"title": obj.title, "url": obj.url, "time": obj.time, "flag": obj.flag}
        return super().default(obj)

class Storage(object):

    def __init__(self, idx_name: str, idxs: list[Index]):
        self.idx_name = idx_name
        self.idxs = idxs
    
    def last_idx(self) -> Index:
        return self.idxs[0]


    def update_idx(self, other_idx):
        pass

    def save(self):
        with open(os.path.join(config.index_dir, self.idx_name + ".idx"), 'w', encoding="utf-8") as f:
            f.write(json.dumps(self, cls=StorageEncoder, ensure_ascii = False))
    
    @staticmethod
    def load_from_local(idx_name: str):
        with open(os.path.join(config.index_dir, idx_name + ".idx"), 'r', encoding="utf-8") as f:
            return json.loads(f.read(), object_hook=Storage.from_dict)

    @classmethod
    def from_dict(cls, d: dict):
        # Index
        if d.get("idxs") is None:
            return Index(d["title"], d["url"], d["time"], d["flag"])
        # Storage
        else:
            return cls(d["idx_name"], d["idxs"])


class BaseSync(object):
    """
    Base class for all sync classes
    """
    def __init__(self, baseurl, index_name) -> None:
        self.baseurl = baseurl
        self.index_name = index_name
        self.storage: Storage = Storage(self.index_name, [])
        pass

    async def parse_page_async(self, text):
        return self.parse_page(text)

    def run(self):
        logger.info("Syncing '{}'".format(self.index_name))
        
        # get local index
        self.storage, last_idx = self.get_local_storage()

        # get remote index
        remote = self.get_remote_storage(last_idx)

        if remote is not None:
            if len(remote.idxs) == 0:
                logger.info("No new records to sync")
                return
            
            logger.info("Find {} records remote to sync".format(len(remote.idxs)))
            # then update local index
            if config.pull or sure():
                self.update_storage(remote)
                self.pull(remote)

        logger.info("Saving local index")
        self.storage.save()
    
    def pull(self, remote_storage: Storage):
        logger.info("Pulling {} records".format(len(remote_storage.idxs)))
        Crawler = crawler[self.index_name]
        work = Crawler()
        urls = [x.url for x in remote_storage.idxs]
        work.run(urls)
        logger.info("Pulling done")

    def get_local_storage(self) -> (Storage, Index):
        if not os.path.exists(config.index_dir):
            os.mkdir(config.index_dir)
        try:
            storage: Storage = Storage.load_from_local(self.index_name)
            logger.info("Local index: {} records".format(len(storage.idxs)))
            return storage, storage.last_idx()
        except:
            logger.info("Local index has no records")
            return Storage(self.index_name, []), None
    
    def update_storage(self, remote_storage: Storage):
        # TODO: Optimize this
        logger.info("Updating local index")
        self.storage.idxs = self.storage.idxs + remote_storage.idxs
        self.storage.idxs = sorted(list(set(self.storage.idxs)), key=lambda x: x.flag, reverse=True)

    def get_remote_storage(self, last_storage):
        pass