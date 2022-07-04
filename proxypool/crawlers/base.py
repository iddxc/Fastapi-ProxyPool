from loguru import logger
from retrying import retry, RetryError
import requests
from fake_headers import Headers
from abc import abstractmethod
from conf.settings import GET_TIMEOUT




class BaseCrawler(object):
    urls = []

    @retry(stop_max_attempt_number=3, retry_on_result=lambda x: x is None, wait_fixed=2000)
    def fetch(self, url, **kwargs):
        try:
            headers = Headers(headers=True).generate()
            kwargs.setdefault("timeout", GET_TIMEOUT)
            kwargs.setdefault("verify", False)
            kwargs.setdefault("headers", headers)
            response = requests.get(url, **kwargs)
            if response.status_code == 200:
                response.encoding = "utf-8"
                return response.text
        except (requests.ConnectionError, requests.ReadTimeout):
            return

    def process(self, html, url):
        for proxy in self.parse(html):
            logger.info(f"fetch Proxy({proxy.string()} from {url})")
            yield proxy

    def crawl(self):
        try:
            for url in self.urls:
                logger.info(f"fetching Url({url})")
                html = self.fetch(url)
                if not html:
                    continue
                yield from self.process(html, url)
        except RetryError:
            logger.error(
                f"Crawler({self}) crawled proxy unsuccessfully, please check if target url is valid or network issue."
            )

    @abstractmethod
    def parse(self, html):
        pass


