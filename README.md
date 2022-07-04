# IP代理池
定时抓取免费代理网站，简易可扩展（代继续更新）。
使用 Redis的 zset类型 对代理给予分数进行可用性排序。
定时测试和筛选，及时删除评分为0的代理，防止无用代理侵扰。
由 Fastapi服务 提供API，随机取用测试通过的可用代理，优先评分最高。

## 使用准备
首先当然是克隆代码并进入 ProxyPool 文件夹：

git clone https://github.com/Python3WebSpider/ProxyPool.git
cd ProxyPool
然后选用下面 Docker 和常规方式任意一个执行即可。

## 使用要求
可以通过两种方式来运行代理池，一种方式是使用 Docker（推荐），另一种方式是常规方式运行，要求如下：

## Docker


## 常规方式
常规方式要求有 Python 环境、Redis 环境，具体要求如下：

Python>=3.6
Redis

### 安装依赖包

然后 pip 安装依赖即可：

``` shell
pip3 install -r requirements.txt
```
### 运行代理池
两种方式运行代理池，一种是 Tester、Getter、Server 全部运行，另一种是按需分别运行。

一般来说可以选择全部运行，命令如下：

``` shell
python3 main.py
```
运行之后会启动 Tester、Getter、Server，这时访问 `http://127.0.0.1:8080/proxy` 即可获取一个随机可用代理。

或者如果你弄清楚了代理池的架构，可以按需分别运行，命令如下：

python3 run.py --processor getter
python3 run.py --processor tester
python3 run.py --processor server
这里 processor 可以指定运行 Tester、Getter 还是 Server。

### 使用
成功运行之后可以通过 `http://127.0.0.1:8080/proxy` 获取一个随机可用代理。

可以用程序对接实现，下面的示例展示了获取代理并爬取网页的过程：
```python
import requests

proxypool_url = 'http://127.0.0.1:5555/random'
target_url = 'http://httpbin.org/get'

def get_random_proxy():
    """
    获取代理IP
    :return: proxy
    """
    return requests.get(proxypool_url).text.strip()

def fetch(url, proxy):
    """
    使用代理获取页面内容
    :param url: page url
    :param proxy: proxy, such as 8.8.8.8:8888
    :return: html
    """
    proxies = {'http': 'http://' + proxy}
    response = requests.get(url, proxies=proxies)
    if response.status_code == 200:
        return response.text
    return 


def main():
    proxy = get_random_proxy()
    print('get random proxy', proxy)
    html = fetch(target_url, proxy)
    print(html)

if __name__ == '__main__':
    main()

```
运行结果如下：
```shell
get random proxy 8.8.8.8:8888
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Host": "httpbin.org",
    "User-Agent": "python-requests/2.22.0",
    "X-Amzn-Trace-Id": "Root=1-5e4d7140-662d9053c0a2e513c7278364"
  },
  "origin": "8.8.8.8:8888",
  "url": "https://httpbin.org/get"
}
```

可以看到成功获取了代理，并请求 httpbin.org 验证了代理的可用性。


## 扩展代理爬虫
代理的爬虫均放置在 proxypool/crawlers 文件夹下，目前对接了有限几个代理的爬虫。

若扩展一个爬虫，只需要在 crawlers 文件夹下新建一个 Python 文件声明一个 Class 即可。

写法规范如下：
```python
from pyquery import PyQuery as pq
from proxypool.schemas.proxy import Proxy
from proxypool.crawlers.base import BaseCrawler

BASE_URL = 'http://www.664ip.cn/{page}.html'
MAX_PAGE = 5

class Daili66Crawler(BaseCrawler):
    """
    daili66 crawler, http://www.66ip.cn/1.html
    """
    urls = [BASE_URL.format(page=page) for page in range(1, MAX_PAGE + 1)]

    def parse(self, html):
        """
        parse html file to get proxies
        :return:
        """
        doc = pq(html)
        trs = doc('.containerbox table tr:gt(0)').items()
        for tr in trs:
            host = tr.find('td:nth-child(1)').text()
            port = int(tr.find('td:nth-child(2)').text())
            yield Proxy(host=host, port=port)
```

在这里只需要定义一个 Crawler 继承 BaseCrawler 即可，然后定义好 urls 变量和 parse 方法即可。

urls 变量即为爬取的代理网站网址列表，可以用程序定义也可写成固定内容。
parse 方法接收一个参数即 html，代理网址的 html，在 parse 方法里只需要写好 html 的解析，解析出 host 和 port，并构建 Proxy 对象 yield 返回即可。
网页的爬取不需要实现，BaseCrawler 已经有了默认实现，如需更改爬取方式，重写 crawl 方法即可。

