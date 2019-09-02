import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

r = requests.post("https://www.veryins.com/user/shenduan0001?next=689493057213409860_601224969&uid=&rg=", headers=headers)
print(r.text)
'''
dat = json.loads(r.text)
nodes = dat['user']['media']['nodes']
item = dict()
item['urls'] = [node['display_src'] for node in nodes]
print(item['urls'])
'''