import logging
from fake_useragent import UserAgent
import requests

logger = logging.getLogger()


class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()

        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())
        request.meta['proxy'] = 'http://' + self.proxy()

    def proxy_json(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def proxy(self):
        # proxy = requests.get("http://127.0.0.1:5010/get").text
        proxy = self.proxy_json().get("proxy")
        try:
            print('get proxy ...')
            # proxy = requests.get("http://127.0.0.1:5010/get").text
            ip = {"http": "http://" + proxy, "https": "https://" + proxy}
            r = requests.get("http://baidu.com", proxies=ip, timeout=4)
            print(r.status_code)
            if r.status_code == 200:
                return proxy
        except Exception as e:
            print('failed reason:{},get proxy again ...'.format(e))
            self.delete_proxy(proxy)
            return self.proxy()

    def process_response(self, request, response, spider):
        # '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            print("again response ip:")
            # 对当前reque加上代理
            request.meta['proxy'] = 'http://' + self.proxy()
            return request
        return response

    def process_exception(self, request, exception, spider):
        logger.debug('Get exception')
        request.meta['proxy'] = 'http://' + self.proxy()
        return request

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
