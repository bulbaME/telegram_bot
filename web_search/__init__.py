import json
import requests
import yaml
from urllib.parse import urlparse

CC = json.load(open('web_search/country_codes.json'))
TOKEN = yaml.safe_load(open('credentials.yaml'))['serper']['token']

def get_country_code_similar(s: str):
    s = s.lower()
    r = None

    for v in CC:
        if v['name'].lower().find(s) != -1:
            r = v['code'].lower()

    return r

def get_sites(country_code: str, query: str, page: int) -> list:
    url = "https://google.serper.dev/search"

    d = json.dumps({
        'q': query,
        'gl': country_code,
        'page': page,
        'num': 100
    })

    headers = {
        'X-API-KEY': TOKEN,
        'Content-Type': 'application/json'
    }

    res = requests.post(url, data=d, headers=headers)

    o = json.loads(res.text)['organic']
    l = set()
    for v in o:
        l.add(v['link'])

    l = list(l)

    def fl(url):
        u = urlparse(url)
        if u.path.count('/') > 1: return False
        return True

    l = list(filter(fl, l))

    return l

def find_by_code(code: str) -> str:
    for o in CC:
        if o['code'].lower() == code.lower():
            return o['name']