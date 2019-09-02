import hashlib
import json
import random
import time
import os
import requests
import sys
from retrying import retry

sys.path.append(os.path.abspath('..'))

from common.proxy.proxy_client import ProxyClient
from renren.settings import REDIS_HOST, REDIS_PORT
from renren.utils.redis_helper import RedisHelper
from renren.utils.try_except import try_except

# 下载图片地址的redis
redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)
DOWNLOADING_LIST = "RRPHOTO_LIST"

download_md5s = set()
MAX_MEM_SIZE = 10 * 1024 * 1024

# 下载根目录
ROOT_PATH = r'Z:\data\renren_photo'

# 历史记录
HISTORY_PATH = os.path.join(ROOT_PATH, r'history.txt')
# 失败记录
FAILURE_PATH = os.path.join(ROOT_PATH, r'failure.txt')

# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
}

# 是否启用代理
ENABLE_PROXY = False


class PicDownloader(object):
    proxy_client = ProxyClient()
    current_proxies = None

    def batch_download(self, dat):
        """
        批次下载
        :param dat:
        :return:
        """
        category = dat['category']
        urls = dat['urls']
        print("## process batch:  {} len:    {}".format(category, len(urls)))

        for url in urls:
            self.download(category, url)
            time.sleep(0.01)

    @try_except
    def download(self, category, url):
        """
        单挑url 下载
        :param category:
        :param url:
        :return:
        """
        print("== current download:  ", url)

        # 分类文件夹
        file_path = time.strftime("%Y%m%d") + os.sep + category
        file_path = os.path.join(ROOT_PATH, file_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # md5 过滤
        md5_hex = hashlib.new('md5', url.encode(encoding='utf-8')).hexdigest()
        if md5_hex in download_md5s:
            print("picture already exits：   ", md5_hex)
            return
        download_md5s.add(md5_hex)

        # 下载文件名
        file_path += os.sep + md5_hex + '.jpg'
        print("current save path:    ", file_path)

        # 下载文件
        try:
            self.retry_timeout(url, file_path)
            # 记录备份
            with open(HISTORY_PATH, 'a+') as f:
                f.write(md5_hex + "\n")
        except Exception as e:
            print("download failure {} ### {}".format(url, e))
            with open(FAILURE_PATH, 'a+') as f:
                f.write(category + ", " + url + "\n")

    # 5秒超时， 最大重试3次
    @retry(stop_max_attempt_number=3)
    def retry_timeout(self, url, save_path):
        """
        下载重试
        :param url:
        :param save_path:
        :return:
        """
        print("try on ", url)
        if ENABLE_PROXY:
            res = self.request_with_proxy(url)
        else:
            res = requests.get(url, timeout=5, headers=headers)

        if len(res.content) <= 0:
            raise Exception("error length")
        with open(save_path, "wb") as f:
            f.write(res.content)

    def request_with_proxy(self, url):
        """
        代理下载
        """
        if self.current_proxies is None or len(self.current_proxies) == 0:
            self.current_proxies = self.proxy_client.get_proxy()
        select_proxy = random.choice(self.current_proxies)
        select_proxy = json.loads(select_proxy)
        try:
            res = requests.get(url, proxies=select_proxy, headers=headers)
            if res.status_code == 200:
                return res
        except Exception as e:
            print(e)
            time.sleep(2)
            self.current_proxies = self.proxy_client.get_proxy()
            raise e


@try_except
def run():
    """
    执行循环
    :return:
    """

    downloader = PicDownloader()
    while True:
        result = redis_helper.list_take(key=DOWNLOADING_LIST)
        if result:
            print("## has data ...")
            dat = json.loads(result)
            downloader.batch_download(dat)
        else:
            print("## list empty ... count: ", len(download_md5s))
            time.sleep(5)
            if len(download_md5s) > MAX_MEM_SIZE:
                print("## clear mem")
                download_md5s.clear()


if __name__ == '__main__':
    print("process start ...")
    run()
    print("process teriminated ..................")
