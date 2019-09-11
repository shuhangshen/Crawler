import inspect
import random
import re

import time

from bs4 import BeautifulSoup


# 杂七杂八

def print_html_body(body):
    soup = BeautifulSoup(body, 'lxml')
    page = soup.prettify()
    print('bs\t', page)


def get_function_name():
    """
    获取当前执行函数名
    :param self:
    :return:
    """
    return inspect.stack()[1][3]


def get_timestamp10():
    """
    获取时间戳10
    :return:
    """
    return int(time.time())


def get_timestamp13():
    """
    获取时间戳10
    :return:
    """
    return int(time.time() * 1000)


class Pretty(object):
    # [update] 20190318. add new char
    # 文章中去掉字符
    re_contents = re.compile(r'[&$^*#|·]')
    # 标题中去掉字符
    re_title = re.compile(r'[&\*#|:：;；\-\+\n"， ]')

    def pretty_contents(self, strings):
        """
        清理内容
        :param strings:
        :return:
        """
        rets = []
        for string in strings:
            ret = re.sub(self.re_contents, " ", string)
            ret = ret.strip()
            if ret is not None and len(ret) != 0:
                rets.append(ret)
        return rets

    def pretty_title(self, string):
        """
        清理标题
        :param string:
        :return:
        """
        if string is None or len(string) == 0:
            return string
        return re.sub(self.re_title, "", string)


USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
    'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
    'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
    'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
    'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
    'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
    'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
    'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
]


def random_user_agent():
    return random.choice(USER_AGENT_LIST)
