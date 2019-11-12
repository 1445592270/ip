import asyncio
import time
from multiprocessing import Process
import aiohttp
from .db import Reids_client
from .settings import *
from .getter import FreeProxyGetter

#验证器
class ValidityTester(object):

    def __init__(self):
        #如果想要校验ip，只需要ip放到这个list中就可以了。
        #为了保证这个list的内容不能随便让人更改，所以把他设为私有。
        #如果设为私有，那就必须要提供一个给外部设置值的方法
        self._raw_proxies = None
        self.headers= {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        }
        #优化，不在这里设置redis连接
        #原因：这个有可能启动后并没有添加数据，这个redis连接对象没用，但是占内存。
        # self._conn = Reids_client()
    def set_raw_proxies(self,proxies):
        self._raw_proxies = proxies
        self._conn = Reids_client()

    # 异步校验一个代理
    async def test_single_proxy(self, proxy):
        # session = aiohttp.ClientSession()
        try:
            async with aiohttp.ClientSession() as session:
                # 校验参数
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                proxy = 'http://' + proxy
                print('开始测试：' + proxy)
                try:
                    async with session.get(TEST_API, headers=self.headers, time_out=PROXY_TEST_TIME_OUT,
                                           proxy=proxy) as response:
                        if response.status == 200:
                            print('有效代理：' + proxy)
                            # 将有效代理存储代理池
                            self._conn.put(proxy)
                except Exception:
                    print('测试代理超时！'+proxy)
        except Exception:
            print('测试代理失败！')

    def test(self):

        print('代理测试程序开始启动！')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_single_proxy(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except Exception as e:
            print(e)

#添加器
class PoolAdder(object):
    def __init__(self,threshold):
        self.threshold = threshold
        self._tester = ValidityTester()
        self._conn = Reids_client()
        self._crawler =FreeProxyGetter()
    '''
    还要做一个逻辑判断，给代理池设置一个最大和最小的阈值，
    如果小于最小值，说明代理不够了，我们就添加，
    如果代理大于最大值，那就说明代理多了，就停止。
    '''
    def is_over_threshold(self):
        if self._conn.queue_len>=self.threshold:
            return True
        else:
            return False

    def add_to_queue(self):
        print('代理池添加器开始工作！')
        proxy_count = 0
        while not self.is_over_threshold():

            #1.从getter.py中的爬虫来获取从网上爬下来的代理。

            '''
                问题：现在只能通过这样方法调用一个网站的方法来获取代理，如果实现
                调用：crawl_xicidaili
                      crawl_aaa
                      crawl_bbb
            for i in list_crawl:
            '''
            # proxies = self._crawler.crawl_xicidaili()
            for i in range(self._crawler.__CrwalCount__):
                callback = self._crawler.__CrawlFunc__[i]
                raw_proxies = self._crawler.get_raw_proxies(callback)
                #2.校验这些代理
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()

                proxy_count+=len(raw_proxies)
                if self.is_over_threshold():
                    print('代理池中可用代理数量已到达上限，请尽快使用！')
                    break

                if proxy_count ==0:
                    print('免费代理网站不可用，请更换网站！')

class Scheduler(object):
    '''
    循环检查代理池的代理数量，如果小于最小值，就说明代理不够了，需要添加，每隔60秒检查一次。
    '''
    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,
                   upper_threshold= POOL_UPPER_THRESHOLD,
                   cycle = POOL_CYCLE_CHECK_TIME):
        conn = Reids_client()
        adder = PoolAdder(upper_threshold)
        while True:
            if conn.queue_len<lower_threshold:
                adder.add_to_queue()
            time.sleep(cycle)

    @staticmethod
    def valid_proxy(cycle = VLLID_CHECK_CYCLE_TIME):
        conn = Reids_client()
        tester = ValidityTester()

        while True:
            print('检查代理池中代理！')
            count = int(0.5*conn.queue_len)
            if count==0:
                print('代理池为空！等待添加！')
                time.sleep(cycle)
                continue
            raw_proxies = conn.get(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)


    def run(self):
        print('代理池开始工作！')
        valid_process = Process(target=Scheduler.valid_proxy)
        check_process = Process(target=Scheduler.check_pool)
        valid_process.start()
        check_process.start()
