import requests
from bs4 import BeautifulSoup
import logging
import os
import json

from regex_processing import check_header

URL = "http://dnd5e.wikidot.com"

#setup logger
logger  = logging.getLogger(__name__)
os.remove("logs/backgrounds_logs.log")
logging.basicConfig(filename="logs/backgrounds_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

def get_backgrounds():
    """
    get the backgrounds from the dnd5ewikidot website.
    """

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")

    page_items = results.find_all("div", class_="row")

    backgrounds = dict()

    for item in page_items:
        if item.find("h3"):
            if check_header(item.find("h3").text, "common backgrounds"):
                background_items = item.find_all("div", class_="col-sm-4")
                for background_item in background_items:
            
                    links = background_item.find_all("a")
                    for link in links:
                        logging.info(f"Found {link.text}")
                        backgrounds[link.text] = get_background_features(link["href"])

    return backgrounds


def get_background_features(background_url):
    """
    Get the features within a background.
    """
    
    background_url = URL + background_url
    logger.info(f"Getting features for {background_url}")
    page = requests.get(background_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find("div", id="page-content")

    features = dict()

    children = results.children

    key = 'Description'
    
    for child in children:
        if child.name == "p":
            logger.info(f"Found {child.text}")
            logger.info(f"Slice is {child.text[:5]}")

            if child.text[:5] == "Skill":
                key = "Skill Proficiencies"
                features[key] = child.text
            else:
                if "Description" in features:
                    features[key] += " " + child.text
                else:
                    if key != 'Description':
                        if key not in features:
                            features[key] = ""
                        else:
                            features[key] += " " + child.text
                    else:
                        features[key] = child.text
        
        if child.name == 'h2':
            key = child.text
            features[key] = ""




    return features



def main():
    backgrounds = get_backgrounds()
    with open("data/backgrounds.json", "w") as f:
        json.dump(backgrounds, f, indent=4)

main()