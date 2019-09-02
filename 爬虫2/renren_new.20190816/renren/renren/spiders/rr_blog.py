# -*- coding: utf-8 -*-
import json
import logging
import re
import traceback

import os
import scrapy
import time
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from renren.items import RenrenBlogItem
from renren.utils.setting import ID_PATH, ROOT_DIR
from renren.utils.tools import get_function_name, Pretty, print_html_body

logger = logging.getLogger()


class RrBlogSpider(scrapy.Spider):
    """
    爬取人人日志
    """
    name = 'rr_blog'
    allowed_domains = ['renren.com']
    start_urls = ['http://renren.com/']

    default_headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0(Windows NT6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Cache-Control': 'max-age=0',
    }

    default_cookie = {
        'anonymid': 'jty44lbakmt05e',
        'depovince': 'ZJ',
        'jebecookies': '243a96f8-a987-4fbe-978a-48bab9479fc1|||||',
        '_r01_': '1',
        'JSESSIONID': 'abcFqX34R0CxAd8aTjmOw',
        'ick_login': '3d330051-4fec-4666-91f3-b802836c840f',
        't': 'e27b6203b524f49a1c19f9508891b4ea2',
        'societyguester': 'e27b6203b524f49a1c19f9508891b4ea2',
        'id': '970389432',
        'xnsid': 'f06ab2d3',
        'ver': '7.0',
        'loginfrom': 'null',
        'wp_fold': '0',
        'jebe_key': '603bf277-8f92-4b09-b881-123dc6275092|ce72829d7d0b078a68b839ea8c39ea26|1554108655094|1|1554271507674'
    }

    default_visit_id = '970389432'
    pt_html_tag = re.compile(r'<[\s\S]+?>')

    pretty = Pretty()

    def start_requests(self):
        root_dir = ROOT_DIR + "\\id\\part1001"
        list_in_path = os.listdir(root_dir)
        list_out_path = []
        # 获取文件夹下所有txt路径
        for i in list_in_path:
            if i == 'id_DL20_2019041119.txt':
                continue
            path = os.path.join(root_dir, i)
            if path.endswith(".txt") and os.path.isfile(path):
                list_out_path.append(path)

        # 逐个txt解析，对每个id 发起请求
        for id_list in list_out_path:
            #id_list = ID_PATH + "\\id\\part1001\\" + "id_DL20_2019041119.txt"
            with open(id_list, "r") as f:
                for line in f:
                    user_id = line.rstrip("\r\n")
                    if len(user_id) == 0:
                        continue
                    page = 1

                    request_url = r'http://blog.renren.com/blog/{}/blogs?categoryId= &curpage={}&null&requestToken=-1639220190&_rtk=6a0c7a7c' \
                        .format(user_id, page)
                    yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers,
                                  method='GET',
                                  callback=self.parse_blog_page, meta={'user_id': user_id, 'page': str(page)})

    def parse_blog_page(self, response):
        """
        解析日志分页
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        try:
            user_id = response.meta['user_id']
            page = response.meta['page']
            dat = json.loads(response.body)
            dat = dat['data']
            if dat is None or len(dat) == 0:
                return

            for blog_info in dat:
                blog_id = int(blog_info['id'])
                # 发起 博客内容请求
                request_url = 'http://blog.renren.com/blog/{}/{}?bfrom=01020110200'.format(user_id, blog_id)
                yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers,
                              method='GET',
                              callback=self.parse_blog_content,
                              meta={'user_id': user_id,
                                    'page': str(page),
                                    'blog_id': str(blog_id)})

            # 发起 下一页博客请求
            page = int(page) + 1
            request_url = r'http://blog.renren.com/blog/{}/blogs?categoryId= &curpage={}&null&requestToken=-1639220190&_rtk=6a0c7a7c' \
                .format(user_id, page)
            yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers,
                          method='GET',
                          callback=self.parse_blog_page, meta={'user_id': user_id, 'page': str(page)})

        except Exception as e:
            traceback.print_exc()
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_blog_content(self, response):
        """
        解析日志内容
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))
        try:
            user_id = response.meta['user_id']
            blog_id = response.meta['blog_id']

            content = response.xpath("//div[@id='blogContent']/descendant-or-self::text()").extract()
            if content is None:
                content = response.xpath("//p/descendant-or-self::text()").extract()
            content = self.pretty.pretty_contents(content)
            content = "\r\n".join(content)
            # 内容为空返回
            if content is None or len(content) == 0:
                return

            # 保存博客
            item = RenrenBlogItem()
            item['url'] = response.url
            item['spider'] = self.name
            item['field'] = time.strftime("%Y%m%d%H")
            item['title'] = user_id + "_" + blog_id
            item['content'] = content
            yield item

            # 发起博客评论请求
            request_url = r'http://comment.renren.com/comment/xoa2?limit=20' \
                          r'&desc=true&offset=0&replaceUBBLarge=true&type=blog' \
                          r'&entryId={}&entryOwnerId={}' \
                          r'&&requestToken=-1639220190&_rtk=6a0c7a7c'.format(blog_id, user_id)
            yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers,
                          method='GET',
                          callback=self.parse_blog_comment, meta={'user_id': user_id, 'blog_id': blog_id})

        except Exception as e:
            traceback.print_exc()
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    def parse_blog_comment(self, response):
        """
        解析日志评论
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        try:
            dat = json.loads(response.body)

            # 解析评论
            comments = dat['comments']
            contents = []
            for comment in comments:
                content = comment['content']
                content = re.sub(self.pt_html_tag, " ", content)
                contents.append(content)
            contents = self.pretty.pretty_contents(contents)
            contents = "\r\n".join(contents)
            if len(contents) == 0:
                return

            # 保存评论
            user_id = response.meta['user_id']
            blog_id = response.meta['blog_id']
            item = RenrenBlogItem()
            item['spider'] = self.name
            item['url'] = response.url
            item['field'] = time.strftime("%Y%m%d%H")
            item['title'] = user_id + "_" + blog_id + "_comments"
            item['content'] = contents
            logger.info("comment item:  ", item)
            yield item

        except Exception as e:
            traceback.print_exc()
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    # def parse(self, response):
    #     pass


def run():
    process = CrawlerProcess()
    process.crawl(RrBlogSpider)
    process.start()


if __name__ == '__main__':
    run()
