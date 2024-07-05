import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from pprint import pprint

from regex_processing import check_header

URL = "http://dnd5e.wikidot.com"

ITEM_DICT = dict()

#setup logger
logger  = logging.getLogger(__name__)
os.remove("logs/items_logs.log")
logging.basicConfig(filename="logs/items_logs.log", encoding= "utf-8", level=logging.DEBUG, format='%(asctime)s - %(message)s')

def get_item_categories():
    """
    Goes to the item section and goes through each category link.
    """

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")

    page_items = results.find_all("div", class_="row")

    for item in page_items:
        if item.find("h1"):
            if check_header(item.find("h1").text, "items"):
                if item.find("a"):
                    item_categories = item.find_all("a")
                    for category in item_categories:
                        category_name = category.text
                        category_url = category["href"]
                        # print(category_name, category_url)
                        if category_name != "Trinkets":
                            logger.info(f"Creating {category_name}")
                            ITEM_DICT[category_name] = get_items(category_url)

def get_items(category_url: str):
    """
    Get items from each page of the category.
    """

    items_dict = dict()
    URL_CATEGORY = URL + category_url
    page = requests.get(URL_CATEGORY)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")

    current_key = category_url[1:]

    if current_key == "wondrous-items":
        #items stored in yui nav table like the spell scraper
        for i in range(8):
            results = soup.find(id="wiki-tab-0-" + str(i))
            item_elements = results.find_all("tr")
            for item in item_elements:
                if item.find("a"):
                    item_name = item.find("a").text
                    item_url = item.find("a")["href"]
                    logger.info(f"Creating {item_name}")
                    items_dict[item_name] = get_item_data(item_url)
        return items_dict
    else:

        for item in results:
            logger.info(f"Checking {item.name}")
            if item.name == "h1" or item.name == "h2":
                logger.info(f"Creating {item.text}")
                item_name = item.text
                current_key = item_name
                items_dict[current_key] = dict()
            
            if item.name == "p":
                logger.info(f"Adding description to {current_key}")
                if len(items_dict) == 0:
                    items_dict[current_key] = dict()
                if "Description" not in items_dict[current_key]:
                    items_dict[current_key]["Description"] = item.text
                else:
                    items_dict[current_key]["Description"] += item.text

            if item.name == 'ul':
                logger.info(f"Adding description list to {current_key}")
                if "Description" not in items_dict[current_key]:
                    items_dict[current_key]["Description"] = item.text
                else:
                    items_dict[current_key]["Description"] += item.text
            
            if item.name == "table":
                logger.info(f"Adding table data to {current_key}")
                if len(items_dict) == 0:
                    items_dict[current_key] = dict()

                table = item.find_all("tr")
                table_headers = list()
                table_data = list()
                for row in table:
                    row_data = row.children
                    table_row = list()
                    for row in row_data:
                        if row.name == "th":
                                table_headers.append(row.text)

                        if row.name == "td":
                            if row.find("a"):
                                for a in row.find_all("a"):
                                    if "href" in a.attrs:
                                        row_url = a["href"]
                                        item_data = dict()
                                        item_data[row.text] = get_item_data(row_url)
                                        table_row.append(item_data)
                            else:
                                table_row.append(row.text)

                                
                            if len(table_row) == len(table_headers):
                                table_data.append(table_row)
                                table_row = list()

                items_dict[current_key]["Table Data"] = table_data
                items_dict[current_key]["Table Headers"] = table_headers

                        
        return items_dict

def get_item_data(item_url: str):
    """
    Given the url of the item, get the item data.
    """
    logger.info(f"Getting item data for {item_url}")
    URL_ITEM = URL + item_url
    page = requests.get(URL_ITEM)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")
    item_data = dict()
    
    for result in results:
        logger.info(f"Checking {result.name}")
        if result.name == "p":
            if "Description" not in item_data:
                item_data["Description"] = result.text 
            else:
                item_data["Description"] += result.text

        if result.name == "ul":
            if "Description" not in item_data:
                item_data["Description"] = result.text
            else:
                item_data["Description"] += result.text

        if result.name == "table":
            table_data = dict()
            table_rows = result.find_all("tr")
            for row in table_rows:
                if row.find("td"):
                    children = row.find_all("td")
                    table_header = children[0].text
                    table_data[table_header] = [child.text for child in children[1:]]

            item_data["Table"] = table_data

    return item_data



def save_item_data():
    """
    Save the item data to a json file.
    """
    get_item_categories() 
    with open("data/items.json", "w") as file:
        json.dump(ITEM_DICT, file, indent=4)

save_item_data()     