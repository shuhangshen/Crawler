# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import Request
import logging
from Jianshu.items import JianshuUserItem

logger = logging.getLogger()


class JianshuUserSpider(scrapy.Spider):
    name = 'jianshu_user'
    allowed_domains = ['jianshu.com']
    # start_urls = ['https://www.jianshu.com/']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        # 'Host': 'www.jianshu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_char = re.compile(r'[?/":*<>|]+')
    match_str = re.compile(r'/follow(.*)')
    match_num = re.compile(r'page=(\d+)')

    def __init__(self):
        print('Enter Init ------')
        super(JianshuUserSpider, self).__init__()

    def __del__(self):
        print("exit ")

    def start_requests(self):
        #根据推荐作者,关注与被关注目录寻找用户特有id
        # 101
        for i in range(1, 2):
            print("***开始分页解析推荐作者栏目,页面:{}***".format(i))
            url = 'https://www.jianshu.com/recommendations/users?page={}'.format(i)
            try:
                yield Request(url=url, headers=self.default_headers, callback=self.parse_author)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url, e))

    def parse_author(self, response):
        author_ids = response.xpath('//div[@class="row"]/div[@class="col-xs-8"]/div/a/@href').extract()
        for author in author_ids:
            #author: "/users/080bb4eac1c9"
            # author_id = re.sub(r'users', 'u', author)
            url_followers = 'https://www.jianshu.com' + author + '/followers'
            url_following = 'https://www.jianshu.com' + author + '/following'
            try:
                yield Request(url=url_followers, headers=self.default_headers,
                              meta={'author_id': author}, callback=self.parse_page)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url_followers, e))
            try:
                yield Request(url=url_following, headers=self.default_headers,
                              meta={'author_id': author}, callback=self.parse_page)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url_following, e))

    def parse_page(self, response):
        # author_id: "/users/080bb4eac1c9"
        author_id = response.meta['author_id']
        # 关注人数
        following = response.xpath('//div[@class="info"]/ul/li[1]/div/a/p/text()').extract_first()
        # 粉丝人数
        followers = response.xpath('//div[@class="info"]/ul/li[2]/div/a/p/text()').extract_first()

        key = re.findall(self.match_str, response.url)[0]
        if key == 'ers':
            #判断有无粉丝
            if int(followers) == 0:
                return
            nums = int(followers) // 18 + 1
            #粉丝小于18，无需翻页
            if int(followers) <= 18:
                url = 'https://www.jianshu.com{}/followers?page=1'.format(author_id)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'key': key}, callback=self.parse)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))
            # 粉丝栏目循环翻页
            for id_num in range(1, int(nums)+1):
                url = 'https://www.jianshu.com{}/followers?page={}'.format(author_id, id_num)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'key': key}, callback=self.parse)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))
        elif key == 'ing':
            #判断有无关注
            if int(following) == 0:
                return
            nums = int(followers) // 18 + 1
            #关注小于18，无需翻页
            if int(following) <= 18:
                url = 'https://www.jianshu.com{}/following?page=1'.format(author_id)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'key': key}, callback=self.parse)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))
            # 关注栏目循环翻页
            for id_num in range(1, int(nums)+1):
                url = 'https://www.jianshu.com{}/following?page={}'.format(author_id, id_num)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'key': key}, callback=self.parse)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))

    #搜索粉丝、关注用户的“粉丝、关注"用户特定id
    def parse(self, response):
        key = response.meta['key']
        item = JianshuUserItem()
        ids = response.xpath('//div[@id="list-container"]/ul/li/div/a/@href').extract()
        item['id'] = ids
        yield item
        # 关注人数
        following = response.xpath('//div[@class="info"]/ul/li[1]/div/a/p/text()').extract_first()
        # 粉丝人数
        followers = response.xpath('//div[@class="info"]/ul/li[2]/div/a/p/text()').extract_first()
        #id: "/u/c481285deb52"
        for id1 in ids:
            author_id = re.sub(r'users', 'u', id1)
            if key == 'ers':
                url = 'https://www.jianshu.com{}/followers?page=1'.format(author_id)
                try:
                    yield Request(url=url, headers=self.default_headers,
                                  meta={'author_id': author_id}, callback=self.parse_page)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))
            elif key == 'ing':
                url = 'https://www.jianshu.com{}/following?page=1'.format(author_id)
                try:
                    yield Request(url=url, headers=self.default_headers,
                                  meta={'author_id': author_id}, callback=self.parse_page)
                except Exception as e:
                    logger.error('{} response failed, Reason:{}'.format(url, e))





