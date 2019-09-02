import json
import random
import time

from retrying import retry

from .request_proxy import RequestProxy
from .setting import SETTING
from common.redis_helper import RedisHelper

redis_helper = RedisHelper(host=SETTING['redis_host'], port=SETTING['redis_port'])


class ProxyClient(object):
    """
    请求代理客户端
    """

    def __init__(self):
        self.request_proxy = RequestProxy()
        self.PROXY_POOL = SETTING['proxy_pool']
        self.ip_pool = list()

    # def pool_proxy(self):
    #     """
    #     not testes 一次拿取所有ip
    #     :return:
    #     """
    #     ret_list = list()
    #     remove_list = list()
    #     if len(self.ip_pool) > 0:
    #         for p in self.ip_pool:
    #             dat = json.loads(p)
    #             if self.request_proxy.check_proxy(proxies=dat):
    #                 ret_list.append(dat)
    #             else:
    #                 remove_list.append(p)
    #         for remove in remove_list:
    #             self.ip_pool.remove(remove)
    #
    #     if len(ret_list) > 0:
    #         return ret_list
    #     else:
    #         self.ip_pool = self.request()
    #         return list(filter(lambda p: self.request_proxy.check_proxy(proxies=json.loads(p)), self.ip_pool))
    #
    # def take_proxy(self):
    #     """
    #     获取代理,生产者消费者
    #     :return:
    #     """
    #     # 先从保存的代理缓存中获取可用代理
    #     while len(self.ip_pool) > 0:
    #         new_proxy = json.loads(self.ip_pool[-1])
    #         self.ip_pool.pop()
    #         if self.request_proxy.check_proxy(proxies=new_proxy):
    #             return new_proxy
    #         else:
    #             time.sleep(2)
    #
    #     # 代理拿空后向redis获取新代理直接使用
    #     if len(self.ip_pool) == 0:
    #         self.ip_pool = self.request()
    #         # 代理负载均衡
    #         random.shuffle(self.ip_pool)
    #     new_proxy = json.loads(self.ip_pool[-1])
    #     self.ip_pool.pop()
    #     return new_proxy

    def get_proxy(self):
        return self.request()

    @retry(stop_max_attempt_number=5)
    def request(self):
        """
        向redis请求代理
        :return:
        """
        curr_list = redis_helper.list_get(key=self.PROXY_POOL)
        if len(curr_list) == 0:
            print("proxy pool empty try later ...")
            time.sleep(5)
            raise Exception("proxy pool empty: ", self.PROXY_POOL)
        return curr_list
