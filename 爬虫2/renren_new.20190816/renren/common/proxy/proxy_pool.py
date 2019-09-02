import json
import time

from retrying import retry

from common.redis_helper import RedisHelper
from .setting import SETTING
from .request_proxy import MogumiaoProxy

redis_helper = RedisHelper(host=SETTING['redis_host'], port=SETTING['redis_port'])


class ProxyPool(object):
    """
    代理管理器
    """

    def __init__(self):
        self.proxyHandler = MogumiaoProxy()
        self.PROXY_POOL = SETTING['proxy_pool']
        self.pool_limit_min = SETTING['pool_LB']

    def update_proxy(self):
        """
        更新redis中的代理池
        :return:
        """
        # 删除无效代理
        if redis_helper.list_len(key=self.PROXY_POOL) > 0:
            print("removing useless proxy")
            curr_list = redis_helper.list_get(key=self.PROXY_POOL)
            remove_list = filter(lambda p: not self.check_proxy(json.loads(p)), curr_list)
            count = 0
            for proxy in remove_list:
                redis_helper.list_remove(key=self.PROXY_POOL, value=proxy)
                count += 1
            print("remove list size:    ", count)

        # 数目不够时申请新代理
        while True:
            curr_size = redis_helper.list_len(key=self.PROXY_POOL)
            print("loop current size:    ", curr_size)
            if curr_size >= self.pool_limit_min:
                break
            new_list = self.request_proxy()
            new_list = filter(lambda p: self.check_proxy(p), new_list)
            for proxy in new_list:
                seq_proxy = json.dumps(proxy)
                redis_helper.list_insert(key=self.PROXY_POOL, elem=seq_proxy)

    @retry(stop_max_attempt_number=3)
    def request_proxy(self):
        """
        请求代理
        :return:
        """
        res = self.proxyHandler.request_proxy()
        if res is None:
            time.sleep(2)
            raise Exception("request proxy failure")
        return res

    def check_proxy(self, proxies):
        return self.proxyHandler.check_proxy(proxies=proxies)
