import time
import os
import schedule

# 封装定时调度

def job(cmd):
    def inner():
        print("Start============", time.strftime("%Y/%m/%d %H:%M:%S"))
        os.system(cmd)
        print("End============")

    return inner


def schedule_run(cmd, *, day, **kwargs):
    """
    启动定时任务
    :param cmd:
    :param day:
    :param kwargs:  when:每天执行时刻
    :return:
    """
    print("start schedule command:  {}  day: {}".format(cmd, day))
    functor = job(cmd)
    when = kwargs['when'] if 'when' in kwargs else "12:00"
    schedule.every(day).days.at(when).do(functor)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule_run("echo hello", day=2)
