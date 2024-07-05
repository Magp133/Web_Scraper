import requests
from bs4 import BeautifulSoup
import json
import logging
import os

from pprint import pprint

URL = "http://dnd5e.wikidot.com"
EXTRA_CLASS_DATA = dict()

logger = logging.getLogger(__name__)
#remove the old logs.
os.remove("logs/extra_class_stuff_logs.log") 
logging.basicConfig(filename="logs/extra_class_stuff_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

def get_class_quicklinks(results: list):
   
    quick_links = {}

    for feature in results:
        if feature.find("h6"):
            links = feature.find_all("h6")
            for link in links:
                if link.text == "Quick Links":
                    link_parent = link.find_parent()
                    for child in link_parent.descendants:
                        if child.name == "a":
                            quick_links[child.text] = child["href"]

    return quick_links

def get_class_quicklink_features(quicklinks: dict):

    features = {}

    for link in quicklinks:
        page = requests.get(URL + quicklinks[link])
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all(class_="feature")
        for result in results:
            if result != "NoneType":
                text = result.text.strip()
            if result.name == "h6" or "h3" or "h2" and text != "\n" and text != " ":
                features[text] = []
            else:
                if len(features) > 0 and text != "\n" and text != " ":
                    features[list(features.keys())[-1]].append(text)
    
    return features


def get_class_table_info():
    """
    These are extra things that the different classes may have.
    These may be things like artificer infusions or eldritch invocations for warlock.
    """
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_="feature")

    class_quicklinks = get_class_quicklinks(results)
    quicklinks_features = get_class_quicklink_features(class_quicklinks)

    # pprint(quicklinks_features.keys())
    class_item_names = list(class_quicklinks.keys())
    class_item_features = list(quicklinks_features.keys())
    # print(class_item_features[0])
    

    for i in range(len(class_item_names)):
        EXTRA_CLASS_DATA[class_item_names[i]] = class_item_features[i]


def write_class_table_info():
    get_class_table_info()
    with open('data/extra_class_info.json', 'w') as outfile:
        json.dump(EXTRA_CLASS_DATA, outfile, indent=4)

write_class_table_info()