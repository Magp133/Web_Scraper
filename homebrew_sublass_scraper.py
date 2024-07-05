import requests
from bs4 import BeautifulSoup
import logging
import os
import json

from regex_processing import check_header

URL = "http://dnd5e.wikidot.com"

#setup logger
logger  = logging.getLogger(__name__)
# os.remove("logs/homebrew_subclasses_logs.log")
logging.basicConfig(filename="logs/homebrew_subclasses_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

def get_subclasses():
    """
    Get all the subclasses from the homebrew section of dnd5ewikidot.
    """
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")

    page_items = results.find_all("div", class_="row")

    homebrew_subclasses = dict()
    #main header is the main class. 
    #the sub header is the homebrew subclass.

    for item in page_items:
        if item.find("h1"):
            logging.info(f"Checking {item.find('h1').text}")
            if check_header(item.find("h1").text, "homebrew subclasses"):
                #find the class="col-sm-4"
                homebrew_classes = item.find_all("div", class_="col-sm-4")
                for homebrew_class in homebrew_classes:
                    key = ''
                    if homebrew_class.find("h6"):
                        logging.info(f"Found {homebrew_class.find('h6').text}")
                        key = homebrew_class.find("h6").text
                        homebrew_subclasses[key] = dict()
                        # print(homebrew_class.find("h6").text)

                    elif homebrew_class.find("h5"):
                        logging.info(f"Found {homebrew_class.find('h5').text}")
                        key = homebrew_class.find("h5").text
                        homebrew_subclasses[key] = dict()
                        # print(homebrew_class.find("h5").text)
                    
                    links = homebrew_class.find_all("a")

                    logger.info(f"Getting subclass features for {key}")
                    for link in links:
                        logging.info(f"Found {link.text}")
                        #use the class features function to get the features of the subclass.
                        homebrew_subclasses[key][link.text] = get_class_features(link["href"])

    return homebrew_subclasses

def get_class_features(class_url):
    
    """
    gets the class features from the class page url addition.

    returns a dict.
    {
    features name: feature description/ {sub features : sub feature description}    
    }

    """

    logger.info(f"Getting class features for {class_url}")

    class_url = URL + class_url
    page = requests.get(class_url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="page-content")

    class_features = results.find(class_="col-lg-12")
    
    if results.find(class_="col-lg-12") == None:
        class_features = results

    features = {}
    sub_features = {}
    adding_sub_feature = False
    adding_feature = False

    feature_name = ""
    sub_feature_name = ""

    for item in class_features:
        if item.name == "h3":
            if adding_sub_feature and item.text != "\n":
                adding_sub_feature = False
                features[feature_name] = sub_features
                sub_features = {}

            
            adding_feature = True
            feature_name = item.text
            features[feature_name] = []
        
        elif item.name == "h5":
            if item.text != "\n":
                adding_feature = False

                adding_sub_feature = True
                sub_feature_name = item.text
                sub_features[sub_feature_name] = []
        
        else:
            if item.text != "\n" and item.name != "table":
                if adding_sub_feature:
                    sub_features[sub_feature_name].append(item.text)
                elif adding_feature:
                    features[feature_name].append(item.text)

    logger.info(f"Finished getting {class_url} features")
    return features

def save_homebrew_subclasses():
    """
    Save the homebrew subclasses to a file.
    """
    homebrew_subclasses = get_subclasses()
    with open("data/homebrew_subclasses.json", "w") as file:
        json.dump(homebrew_subclasses, file)

save_homebrew_subclasses()