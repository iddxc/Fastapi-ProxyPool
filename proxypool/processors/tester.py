import asyncio
import aiohttp
from loguru import logger
from proxypool.schemas import Proxy
from proxypool.storages.redis import RedisClient
from conf.settings import TEST_TIMEOUT, TEST_BATCH, TEST_URL, TEST_VALID_STATUS, TEST_ANONYMOUS
from aiohttp import ClientProxyConnectionError, ServerDisconnectedError, ClientOSError, ClientHttpProxyError,ClientResponseError
from asyncio import TimeoutError

EXCEPTIONS = (
    ClientProxyConnectionError,
    ConnectionRefusedError,
    TimeoutError,
    ServerDisconnectedError,
    ClientOSError,
    ClientHttpProxyError,
    AssertionError,
    ClientResponseError
)


class Tester(object):
    """
    tester for testing proxies in queue
    """
    def __init__(self):
        self.redis = RedisClient()
        self.loop = asyncio.get_event_loop()

    async def test(self, proxy: Proxy):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger.debug(f'testing {proxy}')
                if TEST_ANONYMOUS:
                    async with session.get(TEST_URL, timeout=TEST_TIMEOUT) as response:
                        rsp = await response.json()
                        origin_ip = rsp.get("origin")
                    async with session.get(TEST_URL, proxy=f"http://{proxy.string()}", timeout=TEST_TIMEOUT) as response:
                        rsp = await response.json()
                        anonymous_ip = rsp.get("origin")
                    assert origin_ip != anonymous_ip
                    assert proxy.host == anonymous_ip
                async with session.get(TEST_URL, proxy=f"http://{proxy.string()}",
                                       timeout=TEST_TIMEOUT, allow_redirects=False) as response:
                    if response.status in TEST_VALID_STATUS:
                        self.redis.max(proxy)
                        logger.debug(f"Proxy({proxy}) is valid, set max score")
                    else:
                        self.redis.decrease(proxy)
                        logger.debug(f"Proxy({proxy})is invalid, decrease score")
            except EXCEPTIONS:
                self.redis.decrease(proxy)
                logger.debug(f"Proxy({proxy}) is invalid, decrease score")

    @logger.catch
    def run(self):
        logger.debug("Starting Tester...")
        count = self.redis.count()
        logger.debug(f"Have {count} proxies to test")
        cursor = 0
        while True:
            logger.debug(f"Testing proxies use cursor: {cursor}, count: {TEST_BATCH}")
            cursor, proxies = self.redis.batch(cursor, count=TEST_BATCH)
            if proxies:
                tasks = [self.test(proxy) for proxy in proxies]
                self.loop.run_until_complete(asyncio.wait(tasks))
            if not cursor:
                break

def run_tester():
    host = '96.113.165.182'
    port = '3128'
    tasks = [tester.test(Proxy(host=host, port=port))]
    tester.loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    tester = Tester()
    tester.run()
    # run_tester()

