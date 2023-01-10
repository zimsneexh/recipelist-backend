import requests
import os

from imagesearch import imagesearch
from log import blog

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

class article():

    def __init__(self, json_obj):
        self.id = json_obj["Id"]
        
        pre_commit_languages = json_obj["HasLanguage"]
        self.languages = [ ]
        
        self.api_url = json_obj["Self"]
        self.title = { }
        self.description = { }
        
        # ugly, because ODH returns completely broken datasets..
        for lang in pre_commit_languages:
            _title = json_obj["Detail"][lang].get("Title")
            _description = json_obj["Detail"][lang].get("IntroText")
            
            #
            # check if odh claims object provides lang,
            # while it actually does not
            #
            if(_title is None or _title == ""):
                blog.warn("{} claims to provide lang {}, but does not. ".format(self.id, lang))
            else:
                self.title[lang] = _title
                self.description[lang] = _description
                self.languages.append(lang)

    def get_info_dict(self):
        return {
            "id": self.id,
            "languages": self.languages,
            "title": self.title,
            "description": self.description
        }

    def fetch_details(self):
        pass

    def build_img_cache(self, cache_dir):
        blog.info("Fetching image for {}..".format(self.title[self.languages[0]]))
        target_dir = os.path.join(cache_dir, self.id + ".jpg")

        if(os.path.exists(target_dir)):
            blog.warn("Skipped already existing file")
            return

        search_results = imagesearch.run_search_query(self.title[self.languages[0]])
        print(search_results)
        if(search_results == [ ]):
            blog.warn("No search results for {}..".format(self.title[self.languages[0]]))
            return

        i = 0
        while True:
            try:
                if(len(search_results) < i):
                    blog.warn("No search results for {}..".format(self.title[self.languages[0]]))
                    break

                blog.info("Attempting to fetch image at index {}..".format(i))
                web_rsp = requests.get(search_results[i]["image"], headers=HTTP_HEADERS, timeout=10)
                
                with open(target_dir, "wb") as f:
                    f.write(web_rsp.content)
                break
            except Exception as ex:
                blog.error("Exception raised while attempting to fetch data. Using next image..")
                blog.error("Exception details: {}".format(ex))
                blog.error("Failed link: {}".format(search_results[i]["image"]))
                i = i + 1

        blog.info("Image fetched for {}.".format(self.id))
