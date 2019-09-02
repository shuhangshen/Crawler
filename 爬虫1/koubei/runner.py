import os
from scrapy import cmdline

from koubei.settings import TID_PATH
from koubei.spiders.ckoubei import get_tid_list


def run():
    print("The Paper Run Spider..........")

    tid_list = get_tid_list(TID_PATH)

    # cmdline.execute('scrapy crawl thepaper_front'.split())
    cmd_base = 'scrapy crawl ckoubei'
    for tid in tid_list:
        if tid == '1704':
            print("downloaded 1704")
            continue
        param = ' -a tid={}'.format(tid)
        cmd = cmd_base + param
        # exec one
        # cmdline.execute(cmd.split())
        os.system(cmd)
        print("wait last finish")
    print('The Paper Wait Ends........')


if __name__ == "__main__":
    run()
