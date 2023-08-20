import argparse

def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="BlueFish",
        description="BlueFish - A simple tool for sync and download with crawlers")
    parser.add_argument('-v', '--version', action='store_true', help='the version of BlueFish and remote sources list')
    parser.add_argument('-f', '--force', action='store_true', help='Force to pull all of remote data')
    parser.add_argument('--pull', type=str, default="all", help='Pull which the remote data, default is all')
    parser.add_argument('--proxy', type=str, help='Set the proxy for BlueFish')


    return parser
