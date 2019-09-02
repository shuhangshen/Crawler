import json
import random

import requests

from .setting import SETTING


class RequestProxy(object):
    # 高响应网站列表
    target_urls = [
        'http://httpbin.org/get',
        'http://www.baidu.com',
        'http://cn.bing.com',
        'http://sogou.com',
        'http://www.hao123.com'
    ]
    # 超时大限 10秒
    time_out = SETTING['timeout']

    def request_proxy(self):
        """
        实现接口 请求代理
        :return:
        """
        pass

    def check_proxy(self, *, proxies):
        """
        检测代理连接
        :param proxies:
        :return:
        """
        try:
            target_url = random.choice(self.target_urls)
            print('[check] target_url:  {} proxy:   {}'.format(target_url, proxies))
            res = requests.get(target_url, proxies=proxies, verify=False, timeout=self.time_out)
            return res.status_code == 200
        except Exception as e:
            print(e)
            return False


class MogumiaoProxy(RequestProxy):
    """
    蘑菇代理
    """

    ip_url = r'http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'mvip.piping.mogumiao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    def request_proxy(self):
        res = requests.get(self.ip_url, headers=self.headers)
        if res.status_code != 200:
            return None
        try:
            dat = json.loads(res.text)
            if int(dat['code']) != 0:
                return None
            ret_proxies = list()
            for msg in dat['msg']:
                proxies = {
                    'http': r'http://' + msg["ip"] + ':' + msg["port"],
                    'https': r'https://' + msg["ip"] + ':' + msg["port"],
                }
                ret_proxies.append(proxies)
            return ret_proxies if len(ret_proxies) > 0 else None
        except Exception as e:
            print(e)
            return None
