from bs4 import BeautifulSoup
import requests

default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.guokr.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

r = requests.get("https://www.guokr.com/article/454524/", headers=default_headers)
html = r.text.encode('utf_8')
soup = BeautifulSoup(html, 'lxml')
print(soup.prettify())

