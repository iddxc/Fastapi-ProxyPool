from pyquery import PyQuery as pq
from proxypool.crawlers import BaseCrawler
from proxypool.schemas import Proxy

BASE_URL = "https://www.89ip.cn/index_{page}.html"


class IP89Crawler(BaseCrawler):
    urls = [BASE_URL.format(page=page) for page in range(1, 21)]

    def parse(self, html):
        doc = pq(html)
        trs = doc("tbody tr").items()
        for tr in trs:
            host = tr.find('td:nth-child(1)').text()
            port = int(tr.find('td:nth-child(2)').text())
            yield Proxy(host=host, port=port)


if __name__ == "__main__":
    crawler = IP89Crawler()
    for proxy in crawler.crawl():
        print(proxy)
