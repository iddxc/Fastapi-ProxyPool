from pathlib import Path
import os
import yaml
from loguru import logger

BASE_DIR = str(Path(__file__).parent.parent.resolve())
LOG_DIR = os.path.join(BASE_DIR, "logs")
CONFILE_DIR = os.path.join(BASE_DIR, "conf")
CONFIG_INFO = yaml.safe_load(open(os.path.join(CONFILE_DIR, "config.yaml")))


class RedisConfig(object):
    def __init__(self, host=None, password=None, port=None, username=None, db=None, key=None):
        self.host = host or "127.0.0.1"
        self.password = password
        self.port = port or 6379
        self.username = username or ""
        self.db = db or 0
        self.key = key or ""

    @classmethod
    def from_dict(cls, info: dict):
        obj = cls()
        for k, v in info.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj


class MysqlConfig(object):
    def __init__(self, host=None, password=None, port=None, username=None, db=None, key=None):
        self.host = host or "127.0.0.1"
        self.password = password
        self.port = port or 3600
        self.username = username or ""
        self.db = db or 0

    @classmethod
    def from_dict(cls, info: dict):
        obj = cls()
        for k, v in info.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj


MYSQL_CONF = MysqlConfig.from_dict(CONFIG_INFO.get("mysql"))
REDIS_CONF = RedisConfig.from_dict(CONFIG_INFO.get('redis', None))

PROXY_CONF = CONFIG_INFO.get("proxy", {})
PROXY_SCORE_MAX = PROXY_CONF.get("score_max", 100)
PROXY_SCORE_MIN = PROXY_CONF.get("score_min", 0)
PROXY_SCORE_INIT = PROXY_CONF.get("score_init", 10)
# definition of proxy number
PROXY_NUMBER_MAX = PROXY_CONF.get("number_max", 10000)
PROXY_NUMBER_MIN = PROXY_CONF.get("number_min", 0)

# cycle
CYCLE_CONF = CONFIG_INFO.get("cycle", {})
# definition of tester cycle, it will test every CYCLE_TESTER second
CYCLE_TESTER = CYCLE_CONF.get('tester', 20)
# definition of getter cycle, it will get proxy every CYCLE_GETTER second
CYCLE_GETTER = CYCLE_CONF.get('getter', 100)

DEFAULT_CONF = CONFIG_INFO.get("default", {})
GET_TIMEOUT = DEFAULT_CONF.get('timeout', 10)
# definition of tester
TEST_URL = DEFAULT_CONF.get('test_url', 'https://httpbin.org/ip')
TEST_TIMEOUT = DEFAULT_CONF.get('timeout', 10)
TEST_BATCH = DEFAULT_CONF.get('test_batch', 20)
# only save anonymous proxy
TEST_ANONYMOUS = DEFAULT_CONF.get("anonymous", True)
TEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
}
TEST_VALID_STATUS = DEFAULT_CONF.get("valid_status", [200])

# definition of api
SERVER_CONF = CONFIG_INFO.get('server', {})
API_HOST = SERVER_CONF.get("host", '0.0.0.0')
API_PORT = SERVER_CONF.get('port', 5555)

# flags of enable
ENABLE_TESTER = True
ENABLE_GETTER = True
ENABLE_SERVER = True

LOG_LEVEL_MAP = {
    "DEV_MODE": "DEBUG",
    "TEST_MODE": "INFO",
    "PROD_MODE": "ERROR"
}

APP_ENV = "DEV_MODE"
APP_DEV = IS_DEV = APP_ENV
LOG_LEVEL = LOG_LEVEL_MAP.get(APP_ENV)
ENABLE_LOG_FILE = True
ENABLE_LOG_RUNTIME_FILE = True
ENABLE_LOG_ERROR_FILE = True

if ENABLE_LOG_FILE:
    if ENABLE_LOG_RUNTIME_FILE:
        logger.add(os.path.join(LOG_DIR, "runtime.log"),
                   level=LOG_LEVEL, rotation='1 week', retention='20 days')
    if ENABLE_LOG_ERROR_FILE:
        logger.add(os.path.join(LOG_DIR, 'error.log'), level='ERROR', rotation='1 week')


