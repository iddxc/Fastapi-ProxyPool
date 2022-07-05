import scrapy
from pyquery import PyQuery as pq
from proxypool.items import ProxyItem
from proxypool.schemas import Proxy
from proxypool.storages import store


class Ip89Spider(scrapy.Spider):
    name = 'ip89'
    allowed_domains = ['www.89ip.cn']

    def start_requests(self):
        for i in range(21):
            url = f"https://www.89ip.cn/index_{i}.html"
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response,  **kwargs):
        doc = pq(response.text)
        trs = doc("tbody tr").items()
        for tr in trs:
            item = ProxyItem()
            item["host"] = tr.find('td:nth-child(1)').text()
            item["port"] = tr.find('td:nth-child(2)').text()
            proxy = Proxy(host=item["host"], port=int(item["port"]))
            store.add(proxy)
            self.logger.info(f"fetch Proxy({proxy}) in URL({response.url})")
            yield item

