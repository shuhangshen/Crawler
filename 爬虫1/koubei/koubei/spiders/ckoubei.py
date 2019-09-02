# -*- coding: utf-8 -*-
__author__='lisi8'

import json
import logging
import traceback

import scrapy
import time

from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from koubei.items import KoubeiItem
from koubei.utils.setting import VISIT_URL_PATH
from koubei.utils.tools import get_timestamp13, get_function_name
from koubei.utils.url_manager import UrlManager

logger = logging.getLogger()


class CkoubeiSpider(scrapy.Spider):
    def parse(self, response):
        pass

    name = 'ckoubei'
    allowed_domains = ['koubei.baidu.com']
    start_urls = ['http://koubei.baidu.com/']

    default_headers = {
        'Accept': 'application/json, text/javascript, */*; q = 0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN, zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0(Windows NT6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'koubei.baidu.com',
    }

    url_manager = UrlManager()
    url_manager.load(VISIT_URL_PATH)

    tid = ''

    def __init__(self, *args, **kwargs):
        """
        添加输入参数 kwargs: tid
        :param args:
        :param kwargs:
        """
        super(CkoubeiSpider, self).__init__(*args, **kwargs)
        self.tid = kwargs['tid']

    # 生成指定referer的头
    def generate_headers(self, referer):
        headers = self.default_headers
        headers['Referer'] = referer
        return headers

    # 生成分页请求的
    def generate_get_trademems(self, trade_id, page, timestamp):
        """
        生成请求分类列表页的请求
        :param trade_id: 分类id
        :param page:页数
        :param timestamp:请求时间戳
        :return:
        """
        request_url = r'https://koubei.baidu.com/rank/gettradememsajax?sid=&tradeid={}&childid=0&page={}&_={}' \
            .format(trade_id, page, timestamp)
        referer_url = r'https://koubei.baidu.com/rank?tid={}'.format(trade_id)

        headers = self.generate_headers(referer_url)
        return request_url, headers

    def start_requests(self):
        """
        发起请求
        :return:
        """
        start_page = 1
        start_timestamp = get_timestamp13()
        # trade_list = self.get_tid_list()

        trade_id = '1704'
        trade_id = self.tid

        # for trade_id in trade_list:
        #     # 生成每个子板块的请求
        #     request_url, headers = self.generate_get_trademems(trade_id, start_page, start_timestamp)
        #     meta = {
        #         'trade_id': trade_id,
        #         'start_timestamp': start_timestamp
        #     }
        #
        #     print('start request .. ', request_url)
        #     yield Request(url=request_url, headers=headers, method='GET',
        #                   callback=self.parse_start_page, meta=meta)

        request_url, headers = self.generate_get_trademems(trade_id, start_page, start_timestamp)
        meta = {
            'trade_id': trade_id,
            'start_timestamp': start_timestamp
        }

        print('start request .. ', request_url)
        yield Request(url=request_url, headers=headers, method='GET',
                      callback=self.parse_start_page, meta=meta)

    def parse_start_page(self, response):
        """
        解析按类别 获取商户版块 第一页
        :param response:
        :return:
        """
        try:
            logger.info("{} Url".format(get_function_name(), response.url))
            # 解析 meta 并透传到下一层
            trade_id = response.meta['trade_id']
            start_timestamp = response.meta['start_timestamp']
            datas = json.loads(response.body)

            # 1. 解析总页数
            total_page = int(datas['data']['totalpage'])
            logger.info("{} get page Total  {}".format(get_function_name(), total_page))

            # 2. 解析第一页内容
            logger.info("parse start page ..")
            # 为了使用yield 复用parse

            yield self.parse_gettradememsajax(response)

            if total_page is None or total_page < 2:
                logger.info("parse page ends   {} Total {}".format(response.url, total_page))
                yield

            # 3. 分页请求
            for i in range(2, total_page):
                request_url, headers = self.generate_get_trademems(trade_id, i, start_timestamp)
                logger.info("request page {}".format(request_url))
                yield Request(url=request_url, headers=headers, method='GET',
                              callback=self.parse_gettradememsajax, meta=response.meta)

        except Exception as e:
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_gettradememsajax(self, response):
        """
        解析板块 中每一商户信息
        :param response:
        :return:
        """
        try:
            logger.info("{} Url {}".format(get_function_name(), response.url))

            # 解析meta 透传到下一层
            trade_id = response.meta['trade_id']
            start_timestamp = response.meta['start_timestamp']
            datas = json.loads(response.body)

            results = datas['data']['result']

            for result in results:
                mem_name = result['memname']
                mem_code = result['memcode']
                mem_id = result['memid']
                purl = result['purl']
                meta = {
                    "mem_name": mem_name,
                    "mem_code": mem_code,
                    'mem_id': mem_id,
                    'trade_id': trade_id,
                    'start_timestamp': start_timestamp,
                    'referer_prefix': 'https:' + purl,
                }

                # 从第一页发起请求 获取总页数总页数
                request_url = 'https://koubei.baidu.com/s/getcomtlistajax?memid={}&page=1&isself=0&iscomp=1&fr=site_page_comt&sort=default&praise=all&filter=none&_={}' \
                    .format(mem_id, start_timestamp)
                referer_url = "https:" + purl + "?page=1&tab=comt"
                headers = self.generate_headers(referer_url)

                logger.info("{}  URL {} ".format(get_function_name(), request_url))
                yield Request(url=request_url, headers=headers, method='GET', callback=self.parse_comment_total_page,
                              meta=meta)

        except Exception as e:
            traceback.print_exc()
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_comment_total_page(self, response):
        """
        解析商户信息包含评论总页数 并爬取每一页
        :param response:
        :return:
        """
        try:
            logger.info("{} Url {}".format(get_function_name(), response.url))

            datas = json.loads(response.body)
            total_page = datas['data']['ext']['total']

            refer_prefix = response.meta['referer_prefix']
            start_timestamp = response.meta['start_timestamp']
            mem_id = response.meta['mem_id']

            # 请求 每页评论
            for i in range(1, total_page + 1):
                meta = response.meta

                refer_url = refer_prefix + '?page={}&tab=comt'.format(i)
                # meta 记录实际请求页面需要的信息及分页号
                meta['refer_url'] = refer_url
                meta['target_url'] = \
                    'https://koubei.baidu.com/s/getcomtlistajax?memid={}&page={}&isself=0&iscomp=1&fr=site_page_comt&sort=default&praise=all&filter=none&_={}' \
                        .format(mem_id, i, start_timestamp)
                meta['page'] = i

                headers = self.generate_headers(refer_url)
                request_url = 'https://koubei.baidu.com/mem/getcomtfoldInfoajax?_={}&memid={}&page={}'.format(
                    start_timestamp,
                    mem_id, i)

                yield Request(url=request_url, headers=headers, method='GET', callback=self.parse_recv_total,
                              meta=response.meta)

        except Exception as e:
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_recv_total(self, response):
        """"
        获得空回复之后请求实际页面
        """
        try:
            logger.info("{} Url {}".format(get_function_name(), response.url))

            referer_url = response.meta['refer_url']
            request_url = response.meta['target_url']
            headers = self.generate_headers(referer_url)

            yield Request(url=request_url, headers=headers, method='GET', callback=self.parse_item,
                          meta=response.meta)
        except Exception as e:
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_item(self, response):
        """
        解析商户 每页评论
        :param response:
        :return:
        """

        logger.info("parse comment...................        {}".format(response.url))
        # get update url_manager
        if self.url_manager.url_exist(response.url):
            logger.info("visited url    {}".format(response.url))
            return
        self.url_manager.add_url(response.url)
        self.url_manager.update()

        try:
            mem_name = response.meta['mem_name']
            # mem_code = response.meta['mem_code']
            datas = json.loads(response.body)
            tpl = datas['data']['tpl']
            soup = BeautifulSoup(tpl, 'lxml')

            # 填充字段
            item = KoubeiItem()
            item['url'] = response.url
            item['field'] = response.meta['trade_id']
            item['title'] = mem_name + str(response.meta['page'])
            content = ""
            for pre in soup.find_all('pre'):
                comment = pre.string
                content += comment
                content += "\r\n"
            item['content'] = content

            # logger.info("get item {}".format(item))
            yield item
        except Exception as e:
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))


# tid列表
#tid_path = r'C:\Users\YJY\PycharmProjects\Spider233\koubei\doc\id.txt'


def get_tid_list(tid_path):
    """
    获取tid列表
    :return:
    """
    ret = list()
    with open(tid_path) as file:
        for line in file:
            _, tid, _ = line.split(' ')
            ret.append(tid)
    return ret


# def run():
#     process = CrawlerProcess()
#     process.crawl(CkoubeiSpider, tid=1703)
#     process.start()
#
#
# if __name__ == '__main__':
#     run()

