# Blue Fish

A Crawler with sync and download in local.

Crawl not only the articles content, but aslo the images included. Save as markdown file for local search.With index file, we can sync the remote data and update the new articles.

```text
usage: BlueFish [-h] [-v] [-f] [--pull PULL] [--proxy PROXY]

BlueFish - A simple tool for sync and download with crawlers

options:
  -h, --help     show this help message and exit
  -v, --version  Print the version of BlueFish
  -f, --force    Force to pull all of remote data
  --pull PULL    Pull which the remote data
  --proxy PROXY  Set the proxy for BlueFish
```

## Supported Website

- [x] tttang.com
- [x] xz.aliyun.com
- [ ] weixin platform
- [ ] custom website support

## Usage

Python >= 3.10.x

```sh
pip install -r requirements.txt
python bluefish.py --help

# for example
python bluefish.py --pull xz,tttang --force --proxy socks5://username:pass@127.0.0.1:1080

```

index file is auto generated, pls **don't modify** it.

## Speed

Use `asyncio` and `aiohttp` to speed up the crawler.

But... it's so fast that we may be banned by the website. Just use proxy to avoid it.
Also there is a unsolved problem: [Received "Response payload is not completed" when reading response](https://github.com/aio-libs/aiohttp/issues/4581), it occurs when sending lots of package to same domain.

So, I set `semaphore = asyncio.Semaphore(3)` try to avoid it.

test tttang.com (1580 articles), time costs 1078.92s (about 18min, 0.68s per article)

## Add your own source:

1. Add sync script:

```python

class XZSync(BaseSync):
    def __init__(self):
        super().__init__(baseurl="https://xz.aliyun.com", index_name="xz")

    def parse_page(self, text):
      ...
    
    def get_fully_storage(self):
        ...

    def get_remote_storage(self, last_idx = None):
        ...
        
    def get_total_page(self) -> int:
        ...

```

2. Add download script:

```python
class XZCrawler(BaseCrawler):
    def __init__(self, name = "xz"):
        ...

    async def parse(self, text: str):
        ...

```

3. Add to `main.py`:

```python
crawler = {
    "xz": XZCrawler,
    ...
}
```

4. Enjoy it