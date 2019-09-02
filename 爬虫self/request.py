import requests
import json
from fake_useragent import UserAgent
headers = {
    # "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
}
ua = UserAgent()
headers['User-Agent'] = ua.random
# r = requests.post("https://www.veryins.com/user/ticipinheiro?next=2110395634501799028_11876586&uid=&rg=", headers=headers)
# r = requests.post("https://www.veryins.com/p/B1pf5X0lY3e", headers=headers)


# print(r.text)
# data = json.loads(r.text)
#
# nodes = data['user']['media']['nodes']
#
# item = dict()
# item['url'] = [node['display_src'] for node in nodes]
# print(item['url'])


# 使用免费代理
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


# your spider code
def getHtml(url):
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            html = requests.get(url=url, proxies={"http": "http://{}".format(proxy)}, headers=headers)
            # 使用代理访问
            return html.text
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None


r = getHtml('http://www.dianping.com/')
print(r)

# 参考链接https://github.com/jhao104/proxy_pool
