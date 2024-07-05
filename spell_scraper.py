import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from pprint import pprint

from regex_processing import *




logger = logging.getLogger(__name__)
#remove the old logs.
os.remove("logs/spell_logs.log") 
logging.basicConfig(filename="logs/spell_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

URL_SPELLS = "http://dnd5e.wikidot.com/spells"
SPELL_DICT = dict()

def get_spell_list():
    """
    Scrapes the dnd 5e wiki for all the spells.
    These spells are stored within the SPELL_DICT dictionary.
    The keys are the spell levels (0-9) and the values are dictionaries containing the spell data for that level.
    For each level, the dictionary contains the spell name as the key
    """
    page = requests.get(URL_SPELLS)
    soup = BeautifulSoup(page.content, 'html.parser')
    for i in range(10):
        results = soup.find(id="wiki-tab-0-" + str(i))
        spell_elements = results.find_all('tr')

        spell_level_dict = dict()

        for spell in spell_elements:
            if spell.find('a'):
                spell_name = spell.find('a').text
                logger.info(f"Creating {spell_name}")
                spell_url = spell.find('a')['href']
                logger.info("Started collecting spell data")
                spell_level_dict[spell_name] = spell_data(spell_url)
                logger.info("Finished collecting spell data")
        SPELL_DICT[i] = spell_level_dict

def spell_data(spell_url):
    """"
    Constructs a dictionary containing the spell data for a given spell.
    The data contained is the spell name, level, school, casting time, range, components, duration, and description.
    the spell name and level are the respective keys to reach this data. level: -> spell_name: -> spell_data
    """

    spell_url = URL_SPELLS[:-1] + spell_url[6:]
    page = requests.get(spell_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")
    spell_data = dict()
    headers = results.find_all("strong")
    spell_text = results.find_all("p")
    #source book of the spell
    spell_data["Source"] = spell_text[0].text[8:]

    #spell type including level and school of magic.
    spell_data["Type"] = spell_text[1].text

    #bold text for spell data headers/ keys.
    if len(headers) > 6:
        #want the first 4 headers and the last two headers
        if headers[-2] == "At Higher Levels":
            headers = headers[3:] + headers[-2:]
    else:
        for header in headers:
            spell_data[header.text] = str(header.next_sibling)
    
    #spell classes that can use the spell
    spell_class_lists = headers[-1].next_sibling.next_siblings
    spell_source = ''
    for class_list in spell_class_lists:
        spell_source += class_list.text
    spell_data["Spell Lists."] = spell_source

    #spell description
    #get spell description and any additional information under headers that are not desired headers. 
    #headers are bold text and from 0-3 and the last two if both are present.
    spell_description = ""
    # print(spell_text)
    if headers[-2].text == "At Higher Levels.":
        for i in range(3, len(spell_text)-2):
            spell_description += spell_text[i].text
    else:
        for i in range(3, len(spell_text) - 1):
            spell_description += spell_text[i].text

    if results.find_all("li"):
        for li in results.find_all("li"):
            spell_description += "-" + li.text
    spell_data["Description"] = spell_description

    #perform regex processing on the spell data
    #goal is to add tags to the spell such as crowd control, damage, healing, etc.
    logger.info("Started regex processing")
    spell_data = process_strings(spell_data)
    spell_data = process_hitpoint_values(spell_data)
    logger.info("Finished regex processing")

    return spell_data
    


def write_spell_json():
    """
    Runs the spell data scraper and writes the data to a json file
    """
    get_spell_list()
    with open('data/spells.json', 'w') as outfile:
        json_object = json.dump(SPELL_DICT, outfile)



write_spell_json()