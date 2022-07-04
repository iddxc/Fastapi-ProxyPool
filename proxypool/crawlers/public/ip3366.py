from pyquery import PyQuery as pq
from proxypool.crawlers import BaseCrawler
from proxypool.schemas import Proxy

BASE_URL = "https://proxy.ip3366.net/free/?action=china&page={page}"


class IP3366Crawler(BaseCrawler):
    urls = [BASE_URL.format(page=page) for page in range(1, 6)]

    def parse(self, html):
        doc = pq(html)
        trs = doc("tbody tr").items()
        for tr in trs:
            host = tr.find("td:nth-child(1)").text()
            port = tr.find("td:nth-child(2)").text()
            port = int(port) if port else 0
            if not (host and port):
                continue
            yield Proxy(host=host, port=port)


if __name__ == "__main__":
    crawler = IP3366Crawler()
    for proxy in crawler.crawl():
        print(proxy)