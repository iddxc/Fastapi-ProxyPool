from crochet import setup
setup()
from loguru import logger
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from conf.settings import PROXY_NUMBER_MAX
from proxypool.storages import store
from proxypool.spiders import __all__ as crawlers_cls


class Getter(object):
    def __init__(self):
        self.store = store
        self.crawlers = crawlers_cls

    def is_full(self):
        return self.store.count() >= PROXY_NUMBER_MAX

    @logger.catch
    def run(self):
        if self.is_full():
            return
        runner = CrawlerRunner(get_project_settings())
        for crawler in self.crawlers:
            runner.crawl(crawler)
        runner.join()

if __name__ == "__main__":
    getter = Getter()
    getter.run()
