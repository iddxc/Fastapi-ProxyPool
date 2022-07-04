from loguru import logger

from conf.settings import PROXY_NUMBER_MAX
from proxypool.storages.redis import RedisClient
from proxypool.crawlers import __all__ as crawlers_cls


class Getter(object):
    def __init__(self):
        self.redis = RedisClient()
        self.crawlers = [crawler_cls() for crawler_cls in crawlers_cls]

    def is_full(self):
        return self.redis.count() >= PROXY_NUMBER_MAX

    @logger.catch
    def run(self):
        if self.is_full():
            return
        for crawler in self.crawlers:
            logger.info(f"Crawler({crawler}) to get proxy")
            for proxy in crawler.crawl():
                self.redis.add(proxy)


if __name__ == "__main__":
    getter = Getter()
    getter.run()
