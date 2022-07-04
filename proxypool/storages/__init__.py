from conf.settings import DEFAULT_CONF
from proxypool.storages.redis import RedisClient


class Store(object):
    @classmethod
    def get_store(cls, name="bag_cache"):
        if name.lower() == "redis":
            return RedisClient()


store = Store.get_store(name=DEFAULT_CONF.get("store"))
