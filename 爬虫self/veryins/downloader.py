import hashlib
import json
import time
import os
import requests
from retrying import retry
from veryins.settings import REDIS_HOST, REDIS_PORT
from veryins.utils.redis_helper import RedisHelper
from veryins.utils.try_except import try_except

redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)
VERYINS_LIST = "VERYINS_LIST"

download_md5s = set()
MAX_MEM_SIZE = 10 * 1024 * 1024

ROOT_PATH = r'Z:\data\veryins'
HISTORY_PATH = r'Z:\data\veryins\history.txt'
FAILURE_PATH = r'Z:\data\veryins\failure.txt'


def batch_download(dat):
    """
    批次下载
    :param dat:
    :return:
    """
    category = dat['category']
    urls = dat['urls']
    print("## process batch:  {} len:    {}".format(category, len(urls)))

    for url in urls:
        download(category, url)


@try_except
def download(category, url):
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
        retry_timeout(url, file_path)
        # 记录备份
        with open(HISTORY_PATH, 'a+') as f:
            f.write(md5_hex + "\n")
    except Exception as e:
        print("download failure {} ### {}".format(url, e))
        with open(FAILURE_PATH, 'a+') as f:
            f.write(category + ", " + url + "\n")


# 5秒超时， 最大重试3次
@retry(stop_max_attempt_number=3)
def retry_timeout(url, save_path):
    """
    下载重试
    :param url:
    :param save_path:
    :return:
    """
    print("try on ", url)
    res = requests.get(url, timeout=5)
    if len(res.content) <= 0:
        raise Exception("error length")
    with open(save_path, "wb") as f:
        f.write(res.content)


@try_except
def run():
    """
    执行循环
    :return:
    """
    while True:
        result = redis_helper.list_take(key=VERYINS_LIST)
        if result:
            print("## has data ...")
            dat = json.loads(result)
            batch_download(dat)
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
