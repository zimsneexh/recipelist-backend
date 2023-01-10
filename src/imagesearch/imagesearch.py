import requests
import re
import time
import json

from log import blog

TARGET_REQ_URL = "https://duckduckgo.com/"
TARGET_REQ_API_URL = "https://duckduckgo.com/i.js"
HTTP_HEADERS = {
    'authority': 'duckduckgo.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'sec-fetch-dest': 'empty',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'referer': 'https://duckduckgo.com/',
    'accept-language': 'en-US,en;q=0.9',
}

#
# runs a search query, returns first result str
#
def run_search_query(keyword):
    req_param = {
        'q': keyword
    }

    blog.debug("Sending HTTP request to Duckduckgo")
    vqd = None
    
    while True:
        res = requests.post(TARGET_REQ_URL, data=req_param)
        vqd = re.search(r'vqd=([\d-]+)\&', res.text, re.M|re.I);
        if(vqd is None):
            blog.warn("DuckDuckGo rate limit reached. Waiting.")
            time.sleep(25)
        else:
            break

    blog.debug("Request token obtained: {}".format(vqd))

    params = (
        ('l', 'us-en'),
        ('o', 'json'),
        ('q', keyword),
        ('vqd', vqd.group(1)),
        ('f', ',,,'),
        ('p', '1'),
        ('v7exp', 'a'),
    )

    
    data = None
    while True:
        try:
            res = requests.get(TARGET_REQ_API_URL, headers=HTTP_HEADERS, params=params)
            data = json.loads(res.text)
            break
        except json.decoder.JSONDecodeError:
            blog.warn("DuckDuckGo rate limit reached. Waiting.")
            time.sleep(25)


    blog.debug("Search request completed.")
    return data["results"]
    
