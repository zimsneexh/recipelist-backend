from enum import Enum
import json
import os
import re

from manager import manager
from webserver import webauth
from webserver import webserver
from webserver import usermanager
from dbconnect import database
from log import blog
import main

#
# endpoint class with path and corresponding handler function
#
class endpoint():
    def __init__(self, path, handler):
        self.path = path
        self.handlerfunc = handler
#
# webresponse class with response code and payload
#
class webresponse():
    def __init__(self, wstatus, payload):
        self.status = wstatus.name
        self.response_code = wstatus.value
        self.payload = payload

    def json_str(self):
        return json.dumps({ 
                "status": self.status,
                "response_code": self.response_code,
                "payload": self.payload
            })

class webstatus(Enum):
    SUCCESS = 200
    MISSING_DATA = 300
    SERV_FAILURE = 400
    AUTH_FAILURE = 500

def register_get_endpoints():
    blog.debug("Registering get endpoints..")
    webserver.register_endpoint(endpoint("recipelist", get_recipe_list))
    webserver.register_endpoint(endpoint("", root_endpoint))
    webserver.register_endpoint(endpoint("getimage", get_image))
    webserver.register_endpoint(endpoint("getdetail", get_detail))

def register_post_endpoints():
    blog.debug("Registering post endpoints..")
    webserver.register_post_endpoint(endpoint("auth", auth_endpoint))
    webserver.register_post_endpoint(endpoint("checkauth", check_auth_endpoint))
    webserver.register_post_endpoint(endpoint("logoff", logoff_endpoint))
    webserver.register_post_endpoint(endpoint("createuser", create_user_endpoint))
    webserver.register_post_endpoint(endpoint("addrating", add_rating))

#
# endpoint used to authenticate a user
#
# ENDPOINT /auth (POST)
def auth_endpoint(httphandler, form_data, post_data):
    # invalid request
    if("user" not in post_data or "pass" not in post_data):
        blog.debug("Missing request data for authentication")
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data for authentication")
        return
    
    if(webauth.web_auth().validate_pw(post_data["user"], post_data["pass"])):
        blog.debug("Authentication succeeded.")
        key = webauth.web_auth().new_authorized_key()
        
        httphandler.send_web_response(webstatus.SUCCESS, "{}".format(key.key_id))
    
    else:
        blog.debug("Authentication failure")
        httphandler.send_web_response(webstatus.AUTH_FAILURE, "Authentication failed.")

#
# checks if the user is logged in or not
#
# ENDPOINT /checkauth (POST)
def check_auth_endpoint(httphandler, form_data, post_data):
    if("authkey" not in post_data):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data for authentication.")    
        return
    
    if(webauth.web_auth().validate_key(post_data["authkey"])):
        httphandler.send_web_response(webstatus.SUCCESS, "Authentication succeeded.")
        
    else:
        httphandler.send_web_response(webstatus.AUTH_FAILURE, "Authentication failed.")
        

#
# destroys the specified session and logs the user off
#
# ENDPOINT /logoff (POST)
def logoff_endpoint(httphandler, form_data, post_data):
    if("authkey" not in post_data):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data for authentication.")
        return

    # check if logged in       
    if(webauth.web_auth().validate_key(post_data["authkey"])):
        webauth.web_auth().invalidate_key(post_data["authkey"])
        httphandler.send_web_response(webstatus.SUCCESS, "Logoff acknowledged.")
        
    else:
        httphandler.send_web_response(webstatus.AUTH_FAILURE, "Invalid authentication key.")
        
 
#
# creates a webuser
#
# ENDPOINT /createuser (POST)
def create_user_endpoint(httphandler, form_data, post_data):
    if("cuser" not in post_data or "cpass" not in post_data):
        blog.debug("Missing request data for user creation")
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data for user creation.")
        return
    
    cuser = post_data["cuser"]
    cpass = post_data["cpass"]
    
    if(bool(re.match('^[a-zA-Z0-9]*$', cuser)) == False):
        blog.debug("Invalid username for account creation")
        httphandler.send_web_response(webstatus.SERV_FAILURE, "Invalid username for account creation..")
        return
    
    if(not usermanager.usermanager().add_user(cuser, cpass)):
        httphandler.send_web_response(webstatus.SERV_FAILURE, "User already exists.")
        return

    httphandler.send_web_response(webstatus.SUCCESS, "User created.")

def add_rating(httphandler, form_data, post_data):
    if("authkey" not in post_data):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data for authentication.")
        return

    if("id" not in post_data or "rating" not in post_data or "author" not in post_data):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data. Required: id, rating, author")
        return

    # check if logged in       
    if(webauth.web_auth().validate_key(post_data["authkey"])):
        database.add_rating(post_data["id"], post_data["author"], post_data["rating"])
        httphandler.send_web_response(webstatus.SUCCESS, "Rating added to database.")
    else:
        httphandler.send_web_response(webstatus.AUTH_FAILURE, "Invalid authentication key.")

#
# / endpoint, returns html page
#
# ENDPOINT: / (GET)
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
def get_image(httphandler, form_data):
    if(form_data["getimage"] == ""):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data: article id") 
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
def get_detail(httphandler, form_data):
    if(form_data["getdetail"] == ""):
        httphandler.send_web_response(webstatus.MISSING_DATA, "Missing request data: article id")
        return

    art = manager.manager().get_article_by_id(form_data["getdetail"]) 

    # pass request to ODH
    if(art is None):
        httphandler.send_web_response(webstatus.MISSING_DATA, "No such article.")
        return
    
    httphandler.send_web_response(webstatus.SUCCESS, art.fetch_details())

#
# gets a list of recipes
#
def get_recipe_list(httphandler, form_data):
    req_line = httphandler.headers._headers[0][1]
    recipe_list = [ ]

    for art in manager.manager.recipe_list:
        rp = art.get_info_dict()
        rp["imagelink"] =  "http://" + req_line + "/?getimage=" + rp["id"]
        rp["avgrating"] = database.get_avg_by_id(art.id)
        recipe_list.append(rp)


    httphandler.send_web_response(webstatus.SUCCESS, recipe_list)
    return


