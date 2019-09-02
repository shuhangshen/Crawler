# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging

from scrapy import signals
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import time
import random
import requests
import json

ip_pool = []

logger = logging.getLogger()


class ProxyMiddleware(HttpProxyMiddleware):
    # http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2
    # 维护一个代理IP池，重试时抛弃IP，池中为空时，重新获取一次代理IP
    ip_url = 'http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'Connection': 'keep-alive',
               # 'Cookie': 'td_cookie=180202120; td_cookie=180121702',
               'Host': 'mvip.piping.mogumiao.com',
               'Referer': 'http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    def refresh_ip_pool(self):
        print('更新代理池', time.ctime())
        ip_pool
        while True:
            resp = requests.get(self.ip_url, headers=self.headers)
            print(resp.status_code)
            print(resp.text)

            if resp.status_code != 200:
                time.sleep(2)
                continue
            try:
                json_data = json.loads(resp.text)
                if int(json_data['code']) != 0:
                    time.sleep(2)
                    continue

                for data in json_data['msg']:
                    proxy = 'http://' + data["ip"] + ':' + data["port"]
                    print(proxy)
                    ip_pool.append(proxy)
                break
            except Exception as e:
                time.sleep(2)
                continue

    def process_request(self, request, spider):
        # request.meta['proxy'] = 'https://' + '58.218.92.130:13032'
        # request.meta['proxy'] = 'https://' + '60.255.186.169:8888'  # 高匿名
        if len(ip_pool) == 0:
            self.refresh_ip_pool()

        request.meta['proxy'] = ip_pool[0]
        # print('使用代理中间件', ip_pool[0])
        # 阿布云
        # # 代理服务器
        # proxyServer = "http://http-dyn.abuyun.com:9020"
        # # 代理隧道验证信息
        # proxyUser = "H84906AK792A20UD"
        # proxyPass = "1FA56BB788CC6A9C"
        # proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
        # request.meta["proxy"] = proxyServer
        # request.headers["Proxy-Authorization"] = proxyAuth

        # 蘑菇代理
        # # 代理服务器
        # proxyServer = "http://transfer.mogumiao.com:9001"
        # # appkey为你订单的key
        # proxyAuth = "Basic " + "Qk1naFl6clREdmlIc1htWjpxam5yNkNvR0tYQTZjVXdp"
        # request.meta["proxy"] = proxyServer
        # request.headers["Authorization"] = proxyAuth


class MyRetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        super(MyRetryMiddleware, self).__init__(settings)
        self.logger = logger

    def delete_proxy(self, proxy):
        if proxy:
            try:
                print('旧代理池', ip_pool)
                ip_pool.remove(proxy)
            except Exception as e:
                print(e)
            print('删除代理', proxy, time.ctime())
            print('新代理池', ip_pool)

    def process_response(self, request, response, spider):
        print('my processing retry ...')
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            print('代理失效：', request.meta.get('proxy'))
            self.delete_proxy(request.meta.get('proxy'))
            # time.sleep(random.randint(3, 5))
            self.logger.warning('返回值异常, 进行重试...')
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            # 删除该代理
            print('代理失效：', request.meta.get('proxy'))
            self.delete_proxy(request.meta.get('proxy'))
            # time.sleep(random.randint(3, 5))
            print('连接异常, 进行重试...')
            self.logger.warning('连接异常, 进行重试...')

            return self._retry(request, exception, spider)
        else:
            print("unhandle exception ", exception)
            super(MyRetryMiddleware, self).process_exception(request, exception, spider)
