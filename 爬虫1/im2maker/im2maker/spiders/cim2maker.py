# -*- coding: utf-8 -*-
import json
import logging
import re

import scrapy
import time

from scrapy import Request, FormRequest

from im2maker.items import Im2MakerItem
from im2maker.utils.setting import VISIT_URL_PATH
from im2maker.utils.tools import get_function_name, Pretty
from im2maker.utils.url_manager import UrlManager

logger = logging.getLogger()


class Cim2makerSpider(scrapy.Spider):
    name = 'cim2maker'
    allowed_domains = ['im2maker.com']
    start_urls = ['http://www.im2maker.com/fresh/',
                  'http://www.im2maker.com/science/',
                  'http://www.im2maker.com/design/',
                  'http://www.im2maker.com/question/',
                  'http://www.im2maker.com/industry/',
                  'http://www.im2maker.com/intech/',
                  'http://www.im2maker.com/talk/',
                  'http://www.im2maker.com/investor/',
                  'http://www.im2maker.com/event/',
                  ]

    map_catid = {
        "fresh": "2",
        "science": "4",
        "design": "10",
        "question": "16",
        "industry": "3",
        "intech": "11",
        "talk": "15",
        "investor": "14",
        "event": "17",
    }

    pretty = Pretty()
    url_manager = UrlManager()
    url_manager.load(VISIT_URL_PATH)

    re_subfix = re.compile(r'http://www\.im2maker\.com/(?P<field>[\w]+)/')

    @staticmethod
    def get_timestamp10():
        """
        获取时间戳10
        :return:
        """
        return int(time.time())

    def start_requests(self):
        """
        按板块发起请求
        :return:
        """
        logger.info("start requests")
        request_url = r'http://www.im2maker.com/index.php?m=content&c=index&a=get_more'
        begin = 0
        end = 500

        for url in self.start_urls:

            field = self.re_subfix.search(url).group('field')
            if field not in self.map_catid:
                logger.error("{} failure map    {}".format(get_function_name(), url))
                continue

            headers = {
                'Accept': 'application/json, text/javascript, */*; q = 0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN, zh;q=0.9',
                'Connection': 'keep-alive',
                # 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Host': 'www.im2maker.com',
                'Origin': 'http: //www.im2maker.com',
                'Referer': url,
                'User-Agent': 'Mozilla/5.0(Windows NT6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
                'Cookie': 'PHPSESSID=4u08k0340bup15o1j45af1jef7; Hm_lvt_610a4113e861f3023cb8133ab9f9d7c3=1552707483,1552714513; Hm_lpvt_610a4113e861f3023cb8133ab9f9d7c3=1552714516',
                'X-Requested-With': 'XMLHttpRequest',
            }

            catid = self.map_catid[field]
            last_time = str(self.get_timestamp10())

            if field == 'event':
                # 活动板块
                event_request_url = r'http://www.im2maker.com/index.php?m=content&c=index&a=get_more_event'
                for page_num in range(1, end):
                    data = {
                        "catid": catid,
                        "time": last_time,
                        "city": "0",
                        "type": "0",
                        "pages": str(page_num),
                        "pagesize": "12",
                    }
                    logger.info("{} request URL   {}  [data]  {}".format(get_function_name(),
                                                                         event_request_url, data))
                    yield FormRequest(url=event_request_url, headers=headers, formdata=data, method='POST',
                                      callback=self.parse_ajax_list_event)
            else:
                # 其他板块
                for page_num in range(begin, end):
                    data = {
                        "last_time": last_time,
                        "catid": catid,
                        "pages": str(page_num),
                        "pagesize": "15"
                    }
                    logger.info("{} request URL   {}  [data]  {}".format(get_function_name(),
                                                                         request_url, data))

                    yield FormRequest(url=request_url, headers=headers, formdata=data, method='POST',
                                      callback=self.parse_ajax_list_normal)

    def parse_ajax_list_normal(self, response):
        """
        解析ajax分页请求
        :param response:
        :return:
        """
        logger.info("parse list...................        {}".format(response.url))
        try:
            datas = json.loads(response.body)
            logger.info("response catname   {}".format(datas[0]['catname']))
            for data in datas:
                url = data['url']
                meta = {
                    'title': data['title'],
                    'field': data['catname'],
                    'id': data['id'],
                }
                logger.info("{} Request:    {}".format(get_function_name(), url))
                yield Request(url=url, callback=self.parse_article, meta=meta)

        except Exception as e:
            logger.error("{}    [ERROR]: {} [URL]: {}".format(get_function_name(), e, response.url))

    def parse_ajax_list_event(self, response):
        """
        解析活动 ajax分页请求
        :param response:
        :return:
        """
        logger.info("parse list...................        {}".format(response.url))
        try:
            datas = json.loads(response.body)
            for data in datas:
                url = data['url']
                meta = {
                    'title': data['title'],
                    'field': "活动",
                    'id': data['id'],
                }
                logger.info("{} Request:    {}".format(get_function_name(), url))
                yield Request(url=url, callback=self.parse_article, meta=meta)

        except Exception as e:
            logger.error("{}    [ERROR]: {} [URL]: {}_{}".format(get_function_name(), e,
                                                                 response.url, response.body))

    def parse_article(self, response):
        """
        解析文章
        :param response:
        :return:
        """
        logger.info("parse article...................        {}".format(response.url))

        # get update url_manager
        if self.url_manager.url_exist(response.url):
            logger.info("visited url    {}".format(response.url))
            return
        self.url_manager.add_url(response.url)
        self.url_manager.update()

        try:
            # 提取文件夹名
            field = response.meta['field'] or "NoneType"

            # 获取标题
            title = response.meta['title']
            title = self.pretty.pretty_title(title)
            if title is None or len(title) == 0:
                title = time.strftime("%Y%m%d_%H%M%S")

            # 获取content
            content = response.xpath("//p/text()").extract()
            content = "\r\n".join(self.pretty.pretty_contents(content))
            # 内容为空返回
            if content is None or len(content) == 0:
                return

            item = Im2MakerItem()
            item['url'] = response.url
            item['field'] = field
            item['title'] = title
            item['content'] = content

            logger.info("get item {}".format(item))
            return item
        except Exception as e:
            logger.error("{}    [ERROR]:{}".format(get_function_name(), e))
