import requests
from bs4 import BeautifulSoup
import json
import logging
import os

from pprint import pprint

from regex_processing import check_if_ua, get_trait_names

URL = "http://dnd5e.wikidot.com"

#setup logger
logger  = logging.getLogger(__name__)
os.remove("logs/lineage_logs.log")
logging.basicConfig(filename="logs/lineage_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

#the lineage dict
LINEAGE_DICT = dict()

def get_lineage_list():
    """
    Scrapes the dnd 5e wiki for all the lineages.
    These lineages are stored within the LINEAGE_DICT dictionary.
    The keys are the lineage names and the values are dictionaries containing the lineage data.
    For each lineage, the dictionary contains the lineage name as the key
    """
    page = requests.get(URL + "/lineage")
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")
    lineage_elements = results.find_all('td')

    for lineage in lineage_elements:
        if lineage.find('a'):
            #ignore the custom lineage 
            if lineage.find('a').text != "Custom":
                lineage_name = lineage.find('a').text
                logger.info(f"Creating {lineage_name}")
                lineage_url = lineage.find('a')['href']
                logger.info("Started collecting lineage data")
                if check_if_ua(lineage_url):
                    logger.info(f"{lineage_name} already exists, must be a ua version")
                    lineage_name = lineage_name + " (UA)"
                LINEAGE_DICT[lineage_name] = get_lineage_data(lineage_url, lineage_name)
                logger.info("Finished collecting lineage data")

def get_lineage_data(lineage_url: str, lineage_name: str):
    """
    Given the lineage url, collect the lineage data.
    """
    URL_LINEAGE = URL + lineage_url
    page = requests.get(URL_LINEAGE)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")
    lineage_data = dict()

    #get the lineage description
    if results.find("h1"):
        current_source = results.find("h1").text
    else:
        current_source = "Player's Handbook"
    lineage_data[current_source] = dict()
    current_variation = lineage_name

    lineage_data[current_source][current_variation] = dict()
    


    for child in results.children:
        logger.info(f"Checking {child.name}")
        logger.info(f"Current Source: {current_source}")
        logger.info(f"Current Variation: {current_variation}")

        #if the lineage has multiple sources
        #checks if its a header for a new source
        if child.name == "h1":
            logger.info(f"Adding new source {child.text}")
            current_source = child.text
            lineage_data[current_source] = dict()
            if current_variation == lineage_name:
                lineage_data[current_source][current_variation] = dict()

        #if the lineage has multiple variations
        #checks if its a header for a new variation. Usually from a new source
        if child.name == "h2":
            logger.info(f"Adding new variation {child.text}")
            current_variation = child.text
            lineage_data[current_source][current_variation] = dict()

        #if the lineage has a description
        if child.name == "p":
            logger.info(f"Adding description to {current_variation}")
            logger.info(f"Current dict {lineage_data}")

            if current_variation not in lineage_data[current_source]:
                current_variation = lineage_name + " " + current_source
                logger.info(f"{current_source} no new variation name. New variation set to {current_source}")
                lineage_data[current_source][current_variation] = dict()

            if "Description" not in lineage_data[current_source][current_variation]:
                lineage_data[current_source][current_variation]["Description"] = child.text

        #if the lineage has a list of traits
        if child.name == "ul":
            logger.info(f"Adding traits to {current_variation}")
            traits = child.find('li').text
            key, value = get_trait_names(traits)
            lineage_data[current_source][current_variation][key] = value


        #if the lineage has table data
        if child.name == "table":
            logger.info(f"Adding table data to {current_variation}")
            table_rows = child.find_all("tr")
            table_data = dict()
            for row in table_rows:
                if row.find("td"):
                    children = row.find_all("td")
                    table_header = children[0].text
                    table_data[table_header] = [child.text for child in children[1:]]

            lineage_data[current_source][current_variation]["Table Data"] = table_data


    #remove empty dictionaries
    for source in list(lineage_data.keys()):
        for variation in list(lineage_data[source].keys()):
            if len(lineage_data[source][variation]) == 0:
                del lineage_data[source][variation]


    return lineage_data



def save_lineage_data():
    get_lineage_list()
    with open("data/lineage_data.json", "w") as file:
        json.dump(LINEAGE_DICT, file, indent=4)

save_lineage_data()