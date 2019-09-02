from veryins.utils.schedule_run import schedule_run


def main():
    """
    定时每天执行爬虫
    :return:
    """
    cmd = 'scrapy crawl ins_simple'
    schedule_run(cmd, day=1,when='17:09')
    print("exit ...")


if __name__ == '__main__':
    main()
