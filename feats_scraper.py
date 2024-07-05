import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from pprint import pprint

from regex_processing import check_header

FEAT_DICT = dict()

URL = "http://dnd5e.wikidot.com"

def get_feat_list():
    """
    Scrapes the dnd 5e wiki for all the feats.
    The feats urls are collected and passed to another function.
    Only the official ones. UA and homebrew will be a seperate file.
    """
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")

    feat_elements = results.find_all("div", class_="row")
    
    for item in feat_elements:
        if item.find("h1"):
            if check_header(item.find("h1").text, "feats"):
                if item.find("a"):
                    feats = item.find_all("a")
                    for feat in feats:
                        feat_name = feat.text
                        feat_url = feat["href"]
                        FEAT_DICT[feat_name] = get_feat_info(feat_url)                

def get_feat_info(feat_url: str):
    """
    gets the feat data from the feat url.
    """

    URL_FEAT = URL + feat_url
    page = requests.get(URL_FEAT)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="page-content")
    feat_data = dict()

    for result in results:
        
        
        if result.name == "p":
            #get the feat source
            if "Source:" in result.text:
                feat_data["Source"] = result.text[8:]
            #get feat prerequisites
            elif "Prerequisite:" in result.text:
                feat_data["Prerequisite"] = result.text[13:]
            else:
                if "Description" not in feat_data:
                    feat_data["Description"] = result.text 
                else:
                    feat_data["Description"] += result.text

        #get feat list
        if result.name == "ul":
            if "Description" not in feat_data:
                feat_data["Description"] = result.text
            else:
                feat_data["Description"] += result.text

        #get feat table
        if result.name == "table":
            table_data = dict()
            table_rows = result.find_all("tr")
            for row in table_rows:
                if row.find("td"):
                    children = row.find_all("td")
                    table_header = children[0].text
                    table_data[table_header] = [child.text for child in children[1:]]
            feat_data["Table"] = table_data

    return feat_data


def save_feat_data():
    get_feat_list()
    with open("data/feats.json", "w") as file:
        json.dump(FEAT_DICT, file, indent=4)

save_feat_data()


