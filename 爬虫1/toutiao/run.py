from toutiao.utils.schedule_run import schedule_run


def main():
    """
    定时每天执行爬虫
    :return:
    """
    cmd = 'scrapy crawl tt_selenium'
    schedule_run(cmd, day=1, when='13:52')
    print("exit ...")


if __name__ == '__main__':
    main()
