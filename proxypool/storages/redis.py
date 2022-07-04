import redis

from random import choice
from typing import List

from loguru import logger

from conf.settings import REDIS_CONF, PROXY_SCORE_INIT, PROXY_SCORE_MAX, PROXY_SCORE_MIN
from proxypool.exceptions.empty import PoolEmptyException
from proxypool.schemas.proxy import Proxy

REDIS_CONFIG = {
    'host': REDIS_CONF.host,  # 数据库地址
    'port': REDIS_CONF.port,  # 端口号
    'db': REDIS_CONF.db,  # 数据库名称
    'password': REDIS_CONF.password,  # 数据库密码
}


class RedisPool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    _redis_pool_data = redis.ConnectionPool(decode_responses=True, **REDIS_CONFIG)

    # 实例化redis
    @classmethod
    def get_conn(cls):
        conn = redis.Redis(connection_pool=cls._redis_pool_data)
        return conn


class RedisClient(object):
    def __init__(self):
        self.db = RedisPool.get_conn()

    def add(self, proxy: Proxy, score=PROXY_SCORE_INIT) -> int:
        if not proxy.is_valid_proxy():
            logger.info(f"Proxy({proxy}) is not valid")
            return 0
        if not self.exists(proxy):
            return self.db.zadd(REDIS_CONF.key, {proxy.string(): score})

    def exists(self, proxy: Proxy) -> bool:
        return not self.db.zscore(REDIS_CONF.key, proxy.string()) is None

    def max(self, proxy: Proxy) -> int:
        logger.info(f"{proxy} is valid, set to {PROXY_SCORE_MAX}")
        return self.db.zadd(REDIS_CONF.key, {proxy.string(): PROXY_SCORE_MAX})

    def count(self) -> int:
        return self.db.zcard(REDIS_CONF.key)

    def all(self) -> List[Proxy]:
        return Proxy.convert_proxy_or_proxies(self.db.zrangebyscore(REDIS_CONF.key, PROXY_SCORE_MIN, PROXY_SCORE_MAX))

    def batch(self, cursor, count) -> (int, List[Proxy]):
        cursor, proxies = self.db.zscan(REDIS_CONF.key, cursor, count=count)
        return cursor, Proxy.convert_proxy_or_proxies([i[0] for i in proxies])

    def decrease(self, proxy: Proxy):
        """
        decrease score of proxy, if small than PROXY_SCORE_MIN, delete it
        :param proxy: proxy
        :return: new score
        """

        self.db.zincrby(REDIS_CONF.key, -1, proxy.string())
        score = self.db.zscore(REDIS_CONF.key, proxy.string())
        logger.info(f'{proxy.string()} score decrease 1, current {score}')
        if score <= PROXY_SCORE_MIN:
            logger.info(f'{proxy.string()} current score {score}, remove')
            self.db.zrem(REDIS_CONF.key, proxy.string())

    def random(self) -> Proxy:
        """
        get random proxy
        firstly try to get proxy with max score
        if not exists, try to get proxy by rank
        if not exists, raise error
        :return: proxy, like 8.8.8.8:8
        """
        # try to get proxy with max score
        proxies = self.db.zrangebyscore(
            REDIS_CONF.key, PROXY_SCORE_MAX, PROXY_SCORE_MAX)
        if len(proxies):
            return Proxy.convert_proxy_or_proxies(choice(proxies))
        # else get proxy by rank
        proxies = self.db.zrevrange(
            REDIS_CONF.key, PROXY_SCORE_MIN, PROXY_SCORE_MAX)
        if len(proxies):
            return Proxy.convert_proxy_or_proxies(choice(proxies))
        # else raise error
        raise PoolEmptyException


if __name__ == '__main__':
    pass