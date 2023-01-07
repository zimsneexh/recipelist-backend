import requests
import threading
import json
import os

from log import blog
from article import article
from manager import manager
from webserver import webserver
from webserver import usermanager
from webserver import endpoints

TARGET_INIT_REQ="https://tourism.opendatahub.bz.it/v1/Article?pagesize=1&removenullvalues=true&articletype=32"
TARGET_REAL_REQ="https://tourism.opendatahub.bz.it/v1/Article?pagesize={}&removenullvalues=true&articletype=32"
LISTEN_ADDR="0.0.0.0"
LISTEN_PORT=8080
IMAGE_CACHE_DIR="image-cache"

def main():
    print("Rezept website backend")
    print()
    blog.initialize()

    blog.info("Sending initial webrequest with size=1..")
    num_req_rsp = requests.get(TARGET_INIT_REQ)
    num_req = json.loads(num_req_rsp.text)["TotalResults"]

    blog.info("Resending request with actual length {}..".format(num_req))
    all_articles_rsp = requests.get(TARGET_REAL_REQ.format(num_req))
    all_articles_json = json.loads(all_articles_rsp.text)
     
    # get all 'Items' (articles)
    all_articles = all_articles_json["Items"]
    blog.info("Fetched article-list with {} entries.".format(len(all_articles)))
    
    # parse into articles
    recipe_list = [ ]
    for json_article in all_articles:
        recipe_list.append(article.article(json_article))
   
    manager.manager().add_recipe_list(recipe_list)
    
    blog.info("Building image cache..")
    
    # check for img dir
    if(not os.path.exists(IMAGE_CACHE_DIR)):
        os.mkdir(IMAGE_CACHE_DIR)

    for rcp in manager.manager.recipe_list:
        rcp.build_img_cache(IMAGE_CACHE_DIR)

    # init usermanager
    userm = usermanager.usermanager()

    # register endpoints before webserver starts
    endpoints.register_get_endpoints()
    endpoints.register_post_endpoints()

    blog.info("Starting webserver..")
    
    web_thread = threading.Thread(target=webserver.start_web_server, daemon=True, args=(LISTEN_ADDR, LISTEN_PORT))
    try:
        web_thread.start()
        blog.info("Webserver started. Waiting for requests.")
    except Exception as ex:
        blog.error("Webserver raised Exception: {}")
    
    web_thread.join()

if(__name__ == "__main__"):
    main()
