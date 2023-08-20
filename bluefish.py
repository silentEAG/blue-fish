import argparse
import time

import args
from crawler.tttang import TTTangCrawler
from crawler.xz import XZCrawler
from settings import config
from log import logger
from sync.tttang import TTTangSync
from sync.xz import XZSync

version = "v0.1.0"
banner = f"""BlueFish {version}
"""

"""
sources list
"""
sources = {
    "tttang": TTTangSync,
    "xz": XZSync,
}


class BlueFish(object):

    def __init__(self, arg: argparse.Namespace):
        self.arg = arg

    def sync(self):
        """
        Sync the local with remote index
        """
        logger.info("Syncing...")
        start = time.time()

        syncs = []

        # Set remote sources
        if "all" in config.pull:
            for v in sources.values():
                syncs.append(v())
        else:
            for name in config.pull:
                syncs.append(sources[name]())

        # Run sync
        for sync in syncs:
            sync.run()

        end = time.time()
        logger.info("All syncing done in {:.2f}s".format(end - start))

    @staticmethod
    def parse():
        arg = args.parser().parse_args()
        if arg.version:
            BlueFish.version()
        
        # merge config
        config.merge(arg)
        
        # ready to sync or crawl
        return BlueFish(arg)

    @staticmethod
    def version():
        """
        The version of BlueFish and remote sources list
        """
        sources_list = 'available remote sources: ' + ', '.join(sources.keys())
        print(banner + sources_list)
        exit(0)


if __name__ == '__main__':
    
    bluefish = BlueFish.parse()
    bluefish.sync()
