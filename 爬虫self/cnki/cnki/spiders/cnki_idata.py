# -*- coding: utf-8 -*-
import scrapy
import re
import time
from selenium import webdriver
from scrapy.http import Request

from lxml import etree
from cnki.items import CnkiItem
from cnki.try_except import try_except

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


class CnkiIdataSpider(scrapy.Spider):
    name = 'cnki_idata'
    allowed_domains = ['cn-ki.net']
    start_urls = ['https://www.cn-ki.net/']
    keywords_file = r'Z:\lisi8\keywords.txt'

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'search.cn=ki.net',
        'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    }

    cookies = {
        'ucks': 'xm3SvW5uJw6g4YVKM0GksnyD1q8UBHXz::idata',
        'num': 'shenshuhang0802@163.com',
        'session': 'eyJfcGVybWFuZW50Ijp0cnVlLCJzZWFyY2hfaWQiOnsiIGIiOiJjRlpMUnpKblVuZzFUbWxVY2psMFdBPT0ifX0.EAm_tw.ZSkxoOonJo_6Wndt4PMGdEBrf6w'
    }

    match_num = re.compile(r'\d+')
    user_name = 'shenshuhang0802@163.com'
    password = 'ssh85659608'

    def __init__(self):
        print('Enter Init ------')
        super(CnkiIdataSpider, self).__init__()
        self.options = webdriver.ChromeOptions()
        self.pref = {"profile.managed_default_content_settings.images": 2}  # 不加载图片
        self.options.add_experimental_option("prefs", self.pref)
        #无界面
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        self.bro = webdriver.Chrome(chrome_options=self.options)
        self.wait = WebDriverWait(self.bro, 60)
        self.bro.get('https://www.cn-ki.net/')
        self.log_file = open(r'C:\Users\YJY\Desktop\workspace\cnki\log.txt', 'w', encoding='utf-8')
        print("init end")

    def __del__(self):
        print("exit ")
        self.bro.close()

    def login(self):
        #先自动登陆该网站
        # 进入登陆界面
        btn_search = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//span[@class="mdui-float-right"]/a[@class="mdui-text-color-black-secondary"]')))
        btn_search.click()
        time.sleep(5)
        # 输入用户名和密码，前提是已有账号
        input_search1 = self.wait.until(EC.presence_of_element_located((By.ID, 'num')))
        input_search2 = self.wait.until(EC.presence_of_element_located((By.ID, 'passwd')))
        btn_login = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="flex xs12"]/button')))
        input_search1.clear()
        input_search2.clear()
        input_search1.send_keys(self.user_name)
        input_search2.send_keys(self.password)
        btn_login.click()
        time.sleep(5)
        # 返回搜索界面
        btn_return = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="card__actions"]/button')))
        btn_return.click()
        #跳转到新出现的界面
        self.bro.switch_to.window(self.bro.window_handles[1])
        time.sleep(5)

    @try_except
    def start_requests(self):
        #登陆
        self.login()
        # 遍历关键词
        for keyword in open(self.keywords_file, 'r', encoding='utf-8'):
            keyword = keyword.strip()
            meta = {'keyword': keyword}
            print('开始搜索关键字:%s' % keyword)
            print('开始搜索关键字:%s' % keyword, file=self.log_file)

            #判断当前页面中是否包含<html lang="zh">,另一种<html lang="en">iData开始界面和进入搜索之后界面内的输入框和按键对应的代码不同
            resp = etree.HTML(self.bro.page_source)
            key = resp.xpath('//html/@lang')[0]
            print(key)

            # 将关键词输入到搜索框，点击搜索
            try:
                if key == 'zh':
                    input_search = self.wait.until(EC.presence_of_element_located((By.ID, 'txt_SearchText')))
                    btn_search = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="mainbtn"]')))
                    input_search.clear()
                    input_search.send_keys(keyword)
                    btn_search.click()
                    time.sleep(5)
                    self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="mdui-m-t-0 mdui-m-l-1"]')))
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="pagerTitleCell"]')))
                elif key == 'en':
                    input_search = self.wait.until(EC.presence_of_element_located((By.ID, 'keyword')))
                    btn_search = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="mdui-btn mdui-btn-dense mdui-btn-raised mdui-color-theme-accent"]')))
                    input_search.clear()
                    input_search.send_keys(keyword)
                    btn_search.click()
                    time.sleep(5)
                    self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="mdui-m-t-0 mdui-m-l-1"]')))
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="pagerTitleCell"]')))
            except Exception as reason:
                print('搜索关键词%s出错%s' % (keyword, reason), file=self.log_file)
                self.bro.refresh()
                continue

            # 通过搜索出的总条数，除以每页的条数，得到该关键词的页数
            totalcnt = self.bro.find_element_by_xpath('//div[@class="pagerTitleCell"]')
            totalpage = int(re.findall(self.match_num, totalcnt.text)[0]) / 20 + 1
            print('totalpage is %d---------------' % totalpage)
            # 解析第一页内容，将抓取的url生成Request
            resp = etree.HTML(self.bro.page_source)
            for link in resp.xpath('//h3[@class="mdui-m-t-0 mdui-m-l-1"]/a/@href'):
                url = 'https://search.cn-ki.net' + link
                # url = re.sub(r'/kns', 'kns.cnki.net/KCMS', url, 1)
                yield Request(url=url, method='GET', callback=self.parse, meta=meta)
                time.sleep(0.1)

            # 进入while循环，对上述关键词进行循环翻页并处理
            while True:
                if len(self.bro.find_elements(By.ID, 'main-frame-error')) != 0:
                    print("无法访问网站，back")
                    self.bro.back()
                if len(self.bro.find_elements(By.LINK_TEXT, '504 Gateway Time-out')) != 0:
                    print("网页504超时，back")
                    self.bro.back()
                try:
                    self.wait.until(
                        EC.text_to_be_present_in_element((By.XPATH, '//div[@class="mdui-col-xs-9 TitleLeftCell mdui-valign"]/a[last()]'), '下一页'))
                    btn_next_page = self.bro.find_element_by_xpath('//div[@class="mdui-col-xs-9 TitleLeftCell mdui-valign"]/a[last()]')
                    onclick_attr = btn_next_page.get_attribute('href')
                    print('onclick_attr is {}'.format(onclick_attr))
                    if onclick_attr == None:
                        print('关键词【%s】只有一页 ***' % keyword, file=self.log_file)
                        break
                    current_page = int(re.findall(r'p=(\d+)', onclick_attr)[0])
                    print('current_page is: %d ***current_keywords is %s' % (current_page, keyword))
                    # 当前页数达到总页数前跳出循环。经试验发现，页数超过2w页之后会有问题，因此翻页上限设为低于2w
                    if current_page > totalpage + 1 or current_page > 19900:
                        print('已到最后一页:%d------------' % current_page)
                        print('已到最后一页:%d------------' % current_page, file=self.log_file)
                        break
                    btn_next_page.click()
                    time.sleep(5)  # 由于点击‘下一页’之后页面刷新需要时间，在此显示暂停5秒等待刷新完成。否则会不断停在当前页并不断刷新
                    self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="mdui-m-t-0 mdui-m-l-1"]')))
                except TimeoutException:
                    print('处理关键词[%s]超时******' % keyword, file=self.log_file)
                    print('处理关键词[%s]超时******' % keyword)
                    # try refresh page
                    self.bro.refresh()
                    print("refreshing page ...")
                    break
                except StaleElementReferenceException:
                    print('未刷新完成******')
                    continue
                except Exception as reason:
                    print('未找到下一页:%s' % reason)
                    continue
                resp = etree.HTML(self.bro.page_source)
                for link in resp.xpath('//h3[@class="mdui-m-t-0 mdui-m-l-1"]/a/@href'):
                    url = 'https://search.cn-ki.net' + link
                    # url = re.sub(r'/kns', 'kns.cnki.net/KCMS', url, 1)
                    yield Request(url=url, method='GET', callback=self.parse, meta=meta)
                    time.sleep(0.1)

    @try_except
    def parse(self, response):
        item = CnkiItem()
        title = response.xpath('//span[@class="headline"]/text()').extract()
        # print(title[0])
        # title = response.xpath('//head/title/text()').extract()
        body = response.xpath('//v-card[@class="px-0"]/v-card-text/text()').extract()

        if len(title) == 0 or len(body) == 0:
            print('此url未解析出标题或内容: %s' % response.url)
            print('response body: ', response.body)
        else:
            item['title'] = title[0].strip()
            item['body'] = body
            item['url'] = response.url
            item['keyword'] = response.meta['keyword']
            print(title[0].strip())
            return item
