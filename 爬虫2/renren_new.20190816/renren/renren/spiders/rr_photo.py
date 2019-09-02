# -*- coding: utf-8 -*-
import copy
import json
import logging
import os
import re

import demjson
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from renren.settings import REDIS_HOST, REDIS_PORT
from renren.utils.redis_helper import RedisHelper
from renren.utils.setting import ID_PATH
from renren.utils.tools import print_html_body, get_function_name

logger = logging.getLogger()
redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)
RRPHOTO_LIST = "RRPHOTO_LIST"


class RrPhotoSpider(scrapy.Spider):
    name = 'rr_photo'
    allowed_domains = ['renren.com']
    start_urls = ['http://renren.com/']

    default_headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0(Windows NT6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Cache-Control': 'max-age=0',
    }

    default_cookies = {'anonymid': 'jv0psw8cjps2n5', '_r01_': '1', 'JSESSIONID': 'abcbXe3KyXnL1hQI5zBSw',
                       'ick_login': '1e29705f-5db1-4430-af81-bf21529887db', 'loginfrom': 'null', 'id': '970410296',
                       'ver': '7.0',
                       'jebe_key': '4c15bba5-6ec4-4ddd-9807-a5220c50c6ae%7C51a18f9e2debd610b47e30feae1b7d81%7C1560221383536%7C1%7C1560770185782',
                       'td_cookie': '474024551', 'depovince': 'GW', 't': '9c294dd9e1c2916e75d09f36f2a5ea8a6',
                       'societyguester': '9c294dd9e1c2916e75d09f36f2a5ea8a6', 'xnsid': '9ad962e6', 'wp': '0',
                       'wp_fold': '0', 'jebecookies': '31fef59e-a7da-435c-857a-17dc9ae407a9|||||'}

    match_space = re.compile(r'[\n ]')

    def __init__(self):
        super(RrPhotoSpider, self).__init__()
        self.photo_header = copy.deepcopy(self.default_headers)
        self.photo_header['Accept'] = r'application/json, text/javascript, */*; q=0.01'

    def start_requests(self):
        root_dir = ID_PATH + "\\id\\part1001"
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
            # id_list = ID_PATH + "\\id\\part1001\\" + "id_DL20_2019041119.txt"
            with open(id_list, "r") as f:
                for line in f:
                    user_id = line.rstrip("\r\n")
                    if len(user_id) == 0:
                        continue

                    uid = int(user_id)
                    url = r'http://photo.renren.com/photo/{uid}/albumlist/v7?offset=0&limit=40&showAll=1#'.format(
                        uid=uid)

                    yield Request(url=url, cookies=self.default_cookies, headers=self.default_headers,
                                  callback=self.parse_albumlist,
                                  meta={
                                      'uid': uid,
                                  })

    def parse_albumlist(self, response):
        """
        解析相册列表
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        scripts = response.xpath("//script/text()").extract()
        for script in scripts:
            script = script.strip()
            script = re.sub(self.match_space, "", script)
            script_tag = "nx.webpager.fold"
            # 查找到有相册数据的脚本
            if script.startswith(script_tag):
                script = script.replace("\'", "\"")
                script = script.replace('\/', '/')
                data_photo_tag_begin = "nx.data.photo="
                data_photo_tag_end = "}};"

                # 获取相册字段转json解析
                data_photo_begin_idx = script.find(data_photo_tag_begin)
                data_photo_end_idx = script.find(data_photo_tag_end, data_photo_begin_idx)
                if data_photo_begin_idx != -1 and data_photo_end_idx != -1:
                    data_photo = script[data_photo_begin_idx + len(data_photo_tag_begin):data_photo_end_idx + len(
                        data_photo_tag_end) - 1]
                    dat = demjson.decode(data_photo)

                    album_list = dat['albumList']
                    for album in album_list['albumList']:
                        album_id = album['albumId']
                        owner_id = album['ownerId']
                        source_control = album['sourceControl']

                        # source_ctrl 99 为公开相册
                        if source_control != 99:
                            continue
                        # 相册第一页请求
                        page = 0
                        url = r'http://photo.renren.com/photo/{uid}/album-{album_id}/bypage/ajax/v7?page={page}&pageSize=20&requestToken={token}&_rtk={rtk}'.format(
                            uid=owner_id,
                            album_id=album_id,
                            page=page,
                            token=602123598,
                            rtk=r'efa4aba8')
                        meta = {
                            'uid': owner_id,
                            'album_id': album_id,
                            'page': page,
                        }

                        print("request album {}:{}:{} link:{}".format(meta['uid'], meta['album_id'], meta['page'], url))
                        yield Request(url=url, callback=self.parse_photo_list, headers=self.photo_header,
                                      cookies=self.default_cookies, meta=meta)

    def parse_photo_list(self, response):
        """
        解析相片列表
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        # 从json字段中获取 提取url
        category = str(response.meta['uid']) + os.sep + str(response.meta['album_id'])
        dat = json.loads(response.body)
        if dat['code'] == 0:
            item = dict()
            item['category'] = category
            item['urls'] = [info['url'] for info in dat['photoList']]

            # 转存 redis
            if len(item['urls']) != 0:
                seq_item = json.dumps(item)
                redis_helper.list_insert(key=RRPHOTO_LIST, elem=seq_item)

            # 只要不是最后一页就继续发请求
            if len(item['urls']) == 20:
                meta = copy.deepcopy(response.meta)
                meta['page'] += 1

                url = r'http://photo.renren.com/photo/{uid}/album-{album_id}/bypage/ajax/v7?page={page}&pageSize=20&requestToken={token}&_rtk={rtk}'.format(
                    uid=meta['uid'],
                    album_id=meta['album_id'],
                    page=meta['page'],
                    token=602123598,
                    rtk=r'efa4aba8')

                print("request album {}:{}:{} link:{}".format(meta['uid'], meta['album_id'], meta['page'], url))
                yield Request(url=url, callback=self.parse_photo_list, headers=self.photo_header,
                              cookies=self.default_cookies, meta=meta)


def run():
    process = CrawlerProcess()
    process.crawl(RrPhotoSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl rr_photo')
