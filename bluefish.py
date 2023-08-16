import argparse
import time

import args
from settings import config
from log import logger
from sync.tttang import TTTangSync
from sync.xz import XZSync
from sync import Storage

version = "v0.1.0"
banner = f"""
BlueFish {version}
"""


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

        if "all" in config.pull:
            syncs.append(TTTangSync())
            syncs.append(XZSync())
        else:
            if "tttang" in config.pull:
                syncs.append(TTTangSync())
            if "xz" in config.pull:
                syncs.append(XZSync())

        for sync in syncs:
            sync.run()

        end = time.time()
        logger.info("All syncing done in {:.2f}s".format(end - start))

    def crawler(self):
        """
        Crawl the web
        """
        pass

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
        Print the version of BlueFish
        """
        print(banner)
        exit(0)


if __name__ == '__main__':
    
    bluefish = BlueFish.parse()
    bluefish.sync()
