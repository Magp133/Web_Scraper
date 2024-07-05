import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from pprint import pprint
import re

URL = "http://dnd5e.wikidot.com"


logger = logging.getLogger(__name__)
#remove the old logs.
os.remove("logs/class_logs.log") 
logging.basicConfig(filename="logs/class_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

CLASS_DICT = dict()

def get_class_url(results):
    """
    finds the url for the classes.
    returns a list
    """
    logger.info("Getting class urls")
    class_url = []
    i = 9
    for item in range(i, len(results)):
        if i >= len(results):
            break
        if results[i].find("h1") and results[i].find("h1").find("a"):
            classes = results[i].find("h1").find("a")["href"]
            class_url.append(classes)
        i += 2
    return class_url

def get_class_name(class_url):
    logger.info(f"Getting class name for {class_url}")
    class_url = URL + class_url
    page = requests.get(class_url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(class_="page-title page-header")
    logger.info(f"Finsihed getting {class_url} name")
    return results.text


def get_class_table_info(class_url):
    """
    gets the classes table data from the class url.
    return is the following shape:
    [[level, proficiency bonus, features, special class features, spell levels],
     [],
     [],
     ]
    the rows are filled from 1st to 20th level.

    class special features may be things like artificer infusions or eldritch stuff for warlock.

    """
    class_url = URL + class_url
    logger.info(f"Getting class table info for {class_url}")
    page = requests.get(class_url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="page-content")

    if type(results) != 'NoneType':
        class_table = results.find(class_="wiki-content-table")
        table_data = class_table.find_all("tr")

        table_data.pop(0)

        class_table_text = []
        for item in table_data:
            #row = item.find_all("td")
            row_data = []
            for data in item:
                if data.text == "-":
                    row_data.append("0")
                else:
                    row_data.append(data.text)
            if row_data != []:
                class_table_text.append(row_data)
        logger.info(f"Finished getting {class_url} table info")
        return class_table_text

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


def get_class_archetypes(new_url):
    """
    returns a list of the archetypes url for the class.
    these urls can be processed via the class features function to get the archetype features.
    """
    
    logger.info(f"Getting class archetypes for {new_url}")
    class_url = URL + new_url
    page = requests.get(class_url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(class_ = "col-lg-12").find("table").find_all("a")

 
    pattern = "http://dnd5e.wikidot.com/(.*)"

    all_archetypes = []
    archetype_checker = []

    #get the archetypes with no extra ones that are the same from ua or other sources
    #messy but works
    for result in results:
        if re.search(pattern, result["href"]) != None:
            if result.text not in archetype_checker:
                archetype_checker.append(result.text)
                all_archetypes.append(result["href"].removeprefix("http://dnd5e.wikidot.com"))

    logger.info(f"Finished getting {new_url} archetypes")
    return all_archetypes


def get_class_data():
    """
    Writes the class data to a json file.
    iterates over the classes found in the class='feature'.
    Adds info to the class dict with the class name as the key.
    """
        #get class data
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_="feature")

    class_url = get_class_url(results)
    
    for url in class_url:
        class_name = get_class_name(url)
        class_table_info = get_class_table_info(url)
        class_features = get_class_features(url)
        
        class_archetypes_url = get_class_archetypes(url)
        class_archetypes = []
        archetype_names = []
        for url in class_archetypes_url:
            archetype_names.append(get_class_name(url))
            class_archetypes.append(get_class_features(url))
        
        CLASS_DICT[class_name] = {"Class Table": class_table_info,
                                   "Class Features": class_features
                                   }
        for i in range(len(class_archetypes)):
            CLASS_DICT[class_name][archetype_names[i]] = class_archetypes[i]
        
    
def write_class_data():
    get_class_data()
    with open("data/class_data.json", "w") as outfile:
        json.dump(CLASS_DICT, outfile, indent=3)

# write_class_data()