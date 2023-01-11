import requests
import os

from imagesearch import imagesearch
from log import blog

import main
import json

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

class article_detail():

    def __init__(self, json_resp, languages):
        self.languages = languages
        self.title = { }
        self.ingredients = { }
        self.recipe_text = { }
        self.tipp_text = { }

        # fetch all titles 
        for lang in self.languages:
            self.title[lang] = json_resp["Detail"][lang]["Title"]

        # default value
        self.time_required = "No time requirement set."
        
        for lang in self.languages:
            time_pre_commit = None

            try:
                time_pre_commit = json_resp["AdditionalArticleInfos"][lang]["Elements"]["zeit"]
            except KeyError:
                pass

            if(time_pre_commit is None):
                blog.warn("FIXUP! Article in lang {} doesn't provide time requirement.. Checking next index.".format(lang))
                continue
            
            self.time_required = time_pre_commit
            break
       
        self.author_name = "No author set."

        for lang in self.languages:
            author_pre_commit = None
            
            try:
                author_pre_commit = json_resp["AdditionalArticleInfos"][lang]["Elements"]["author"]
            except KeyError:
                pass

            if(author_pre_commit is None):
                blog.warn("FIXUP! Article in lang {} doesn't provide author.. Checking next index.".format(lang))
                continue
            
            self.author_name = author_pre_commit
            break
        

        for lang in self.languages:
            self.ingredients[lang] = "No ingredients set."
            self.tipp_text[lang] = "No tipptext set."
            self.recipe_text[lang] = "No recipetext set."

            try:
                self.ingredients[lang] = json_resp["AdditionalArticleInfos"][lang]["Elements"]["zutat1"]
            except KeyError:
                pass
            
            try:
                self.tipp_text[lang] = json_resp["AdditionalArticleInfos"][lang]["Elements"]["tipptext"]
            except KeyError:
                pass
                
            try:
                self.recipe_text[lang] = json_resp["AdditionalArticleInfos"][lang]["Elements"]["zutat1"]
            except KeyError:
                pass


        #self.additional_text = additional_text

    def get_info_dict(self):
        return {
            "languages": self.languages,
            "title": self.title,
            "ingredients": self.ingredients,
            "recipetext": self.recipe_text,
            "tipptext": self.tipp_text
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
                blog.warn("FIXUP: {} claims to provide lang {}, but doesn't.".format(self.id, lang))
            else:
                self.title[lang] = _title
                self.description[lang] = _description
                self.languages.append(lang)

    

    def get_info_dict(self):
        
        return {
            "id": self.id,
            "languages": self.languages,
            "title": self.title,
            "description": self.description,
        }

    def fetch_details(self):
        blog.info("Passing request to ODH")
        odh_resp = json.loads(requests.get(self.api_url).text)

        return article_detail(odh_resp, self.languages).get_info_dict() 
        


    def build_img_cache(self, cache_dir):
        target_dir = os.path.join(cache_dir, self.id + ".jpg")

        if(os.path.exists(target_dir)):
            return


        title_sq = self.title[self.languages[0]]

        blog.info("Fetching image for {}..".format(title_sq))
        search_results = imagesearch.run_search_query(title_sq)
        if(search_results == [ ]):
            blog.warn("No search results for {}..".format(title_sq))
            return

        i = 0
        while True:
            try:
                if(len(search_results) < i):
                    blog.warn("No search results for {}..".format(title_sq))
                    break

                blog.info("Attempting to fetch image at index {}..".format(i))
                web_rsp = requests.get(search_results[i]["image"], headers=HTTP_HEADERS, timeout=10)
                
                with open(target_dir, "wb") as f:
                    f.write(web_rsp.content)
                break
            except Exception as ex:
                blog.error("Exception raised while attempting to fetch data. Using next image..")
                blog.error("Exception details: {}".format(ex))
                blog.error("Failed link: {}".format(search_results[i]["thumbnail"]))
                i = i + 1

        blog.info("Image fetched for {}.".format(self.id))
