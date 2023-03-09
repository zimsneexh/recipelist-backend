from enum import Enum
import json
import os
import re

from manager import manager
from branchweb import usermanager
from dbconnect import database
import blog
from branchweb import webserver
from branchweb import webauth
import main

class recipe_web_providers():

    @staticmethod
    def get_get_providers():
        get_providers = {
            "recipelist": recipe_web_providers.get_recipe_list,                 
            "": recipe_web_providers.root_endpoint,
            "getimage": recipe_web_providers.get_image,
            "getdetail": recipe_web_providers.get_detail
        }
        return get_providers

    @staticmethod
    def get_post_providers():
        post_providers = {
            "auth": recipe_web_providers.auth_endpoint,
            "checkauth": recipe_web_providers.check_auth_endpoint,
            "logoff": recipe_web_providers.logoff_endpoint,
            "createuser": recipe_web_providers.create_user_endpoint,
            "addrating": recipe_web_providers.add_rating
        }
        return post_providers
        

    #
    # endpoint used to authenticate a user
    #
    # ENDPOINT /auth (POST)
    @staticmethod
    def auth_endpoint(httphandler, form_data, post_data):
        # invalid request
        if("user" not in post_data or "pass" not in post_data):
            blog.debug("Missing request data for authentication")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication")
            return
        

        if(webauth.web_auth().validate_pw(post_data["user"], post_data["pass"])):
            blog.debug("Authentication succeeded.")
            key = webauth.web_auth().new_authorized_key()
            
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "{}".format(key.key_id))
        
        else:
            blog.debug("Authentication failure")
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Authentication failed.")

    #
    # checks if the user is logged in or not
    #
    # ENDPOINT /checkauth (POST)
    @staticmethod
    def check_auth_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication.")    
            return
        
        if(webauth.web_auth().validate_key(post_data["authkey"])):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Authentication succeeded.")
            
        else:
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Authentication failed.")
            

    #
    # destroys the specified session and logs the user off
    #
    # ENDPOINT /logoff (POST)
    @staticmethod
    def logoff_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication.")
            return

        # check if logged in       
        if(webauth.web_auth().validate_key(post_data["authkey"])):
            webauth.web_auth().invalidate_key(post_data["authkey"])
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Logoff acknowledged.")
            
        else:
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            
     
    #
    # creates a webuser
    #
    # ENDPOINT /createuser (POST)
    @staticmethod
    def create_user_endpoint(httphandler, form_data, post_data):
        if("cuser" not in post_data or "cpass" not in post_data):
            blog.debug("Missing request data for user creation")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for user creation.")
            return
        
        cuser = post_data["cuser"]
        cpass = post_data["cpass"]
        
        if(bool(re.match('^[a-zA-Z0-9]*$', cuser)) == False):
            blog.debug("Invalid username for account creation")
            httphandler.send_web_response(webserver.webstatus.SERV_FAILURE, "Invalid username for account creation..")
            return
        
        if(not usermanager.usermanager().add_user(cuser, cpass)):
            httphandler.send_web_response(webserver.webstatus.SERV_FAILURE, "User already exists.")
            return

        httphandler.send_web_response(webserver.webstatus.SUCCESS, "User created.")

    def add_rating(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication.")
            return

        if("id" not in post_data or "rating" not in post_data or "author" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data. Required: id, rating, author")
            return

        # check if logged in       
        if(webauth.web_auth().validate_key(post_data["authkey"])):
            if(not database.add_rating(post_data["id"], post_data["author"], post_data["rating"])):
                httphandler.send_web_response(webserver.webstatus.SERV_FAILURE, "User {} already rated this article.".format(post_data["author"]))
                return

            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Rating added to database.")
        else:
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")

    #
    # / endpoint, returns html page
    #
    # ENDPOINT: / (GET)
    @staticmethod
    def root_endpoint(httphandler, form_data):
        httphandler.send_response(200)
        httphandler.send_header("Content-type", "text/html")
        httphandler.end_headers()

        httphandler.wfile.write(bytes("<html>", "utf-8"))
        httphandler.wfile.write(bytes("<h1>Nope.</h1>", "utf-8"))
        httphandler.wfile.write(bytes("</html>", "utf-8"))

    #
    # get an image
    #
    @staticmethod
    def get_image(httphandler, form_data):
        if(form_data["getimage"] == ""):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data: article id") 
            return

        img_path = os.path.join(main.IMAGE_CACHE_DIR, "{}.jpg".format(form_data["getimage"]))

        if(os.path.exists(img_path)):
            with open(img_path, "rb") as f:
                httphandler.send_file(f, os.path.getsize(img_path), "image.jpg")
        else:
            with open("no_result.jpg", "rb") as f:
                httphandler.send_file(f, os.path.getsize("no_result.jpg"), "image.jpg")


    #
    # get detail
    #
    @staticmethod
    def get_detail(httphandler, form_data):
        if(form_data["getdetail"] == ""):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data: article id")
            return

        art = manager.manager().get_article_by_id(form_data["getdetail"]) 

        # pass request to ODH
        if(art is None):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "No such article.")
            return
        
        details = art.fetch_details()

        # get imagelink
        req_line = httphandler.headers._headers[0][1]
        details["imagelink"] = "http://" + req_line + "/?getimage=" + art.id
        details["avgrating"] = database.get_avg_by_id(art.id)

        httphandler.send_web_response(webserver.webstatus.SUCCESS, details)

    #
    # gets a list of recipes
    #
    @staticmethod
    def get_recipe_list(httphandler, form_data):
        req_line = httphandler.headers._headers[0][1]
        recipe_list = [ ]

        for art in manager.manager.recipe_list:
            rp = art.get_info_dict()
            rp["imagelink"] =  "http://" + req_line + "/?getimage=" + rp["id"]
            rp["avgrating"] = database.get_avg_by_id(art.id)
            recipe_list.append(rp)


        httphandler.send_web_response(webserver.webstatus.SUCCESS, recipe_list)
