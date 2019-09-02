import os
import sys
import time
import traceback

import schedule

sys.path.append(os.path.abspath('..'))
from common.proxy.proxy_pool import ProxyPool
from common.proxy.setting import SETTING

# global proxy pool
proxy_pool = ProxyPool()


def loop_update_proxy():
    try:
        print("**** update proxy on ", time.strftime("%m/%d %H:%M:%S"))
        proxy_pool.update_proxy()
        print("**** end update on ", time.strftime("%m/%d %H:%M:%S"))
    except Exception as e:
        traceback.print_exc()
        print("***** unhandle exception: ", e)


def run():
    # 定时三秒执行 刷新
    print("start proxy agent .. duration: ", SETTING['duration'])
    schedule.every(SETTING['duration']).seconds.do(loop_update_proxy)
    # schedule.every(3).minutes.do(loop_update_proxy)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    run()
