import requests
from bs4 import BeautifulSoup
import re

URL = "http://dnd5e.wikidot.com"
URL_SPELLS = "http://dnd5e.wikidot.com/spells"


def convert_data_to_string(data):
    new_data = ""
    for item in data:
        if item != "\n":
            new_data += item + "/"

    return new_data

##################################################################################################################
#Spell Section
##################################################################################################################


def get_spell_info(url_addition):
    #given a url addition, returns the data from the page
    page = requests.get(URL + url_addition)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="page-content")

    if results.text:
        results_list = results.text.split("\n")
        index = 0
        #cleans the data by removing blank entries
        for item in range(len(results_list)):
            if results_list[index] == '':
                results_list.pop(index)
            else:
                index += 1
        return results_list


def get_spell_data(results, level = 0):
    """
        First entry spell name                            0
        second entry source book                          1
        third entry school and level                      2
        fourth entry casting time                         3
        fifth entry range                                 4
        sixth entry components                            5
        seventh entry duration                            6
        eights entry description                          7
        ninth entry higher level (if exists)              8
        last entry spell list/ classes that use them     -1
    """


    spell_elements = results.find_all("tr")
    if level == 0:
        write_type = "w"
    else:
        write_type = "a"
    with open("spells.txt", write_type) as f:
        for spell in spell_elements:
            if spell.find("a"):
                spell_info = spell.find("a")
                spell_link = spell_info["href"]
                spell_name = [str(level), spell_info.text]
                spell_info = get_spell_info(spell_link)
                spell_data = spell_name + spell_info
                f.write(convert_data_to_string(spell_data))
                f.write("\n")

##################################################################################################################
#Class Section
##################################################################################################################

def get_class_url(results):
    """
    finds the url for the classes.
    currently returns the first one
    """
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
    class_url = URL + class_url
    page = requests.get(class_url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(class_="page-title page-header")
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
        return class_table_text

def get_class_features(class_url):
    
    """
    gets the class features from the class page url addition.

    returns a dict.
    {
    features name: feature description/ {sub features : sub feature description}    
    }

    """

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

    return features


def get_class_archetypes(new_url):
    """
    returns a list of the archetypes url for the class.
    these urls can be processed via the class features function to get the archetype features.
    """
    
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

    return all_archetypes


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



##################################################################################################################
#Writing to file
##################################################################################################################
        
def write_spells_to_file():
    """
    the get spell data gets and writes to file without storing a lot of data. 
    easier to do than return lots of strings.
    """

    page = requests.get(URL_SPELLS)
    soup = BeautifulSoup(page.content, "html.parser")
    for i in range(10):
        results = soup.find(id="wiki-tab-0-" + str(i))
        get_spell_data(results, i)

def write_classes_to_file(class_name: str, class_table_info: list, class_features: dict, archetype_names: list, class_archetypes: list, entry = 0):
    """
    write the class to file.
    class name
    class table
    class features
    gap
    """
    if entry == 0:
        write_type = "w"
    else:
        write_type = "a"

    with open("classes.txt", write_type) as f:
        f.write(class_name)
        f.write("\n")
        for row in class_table_info:
            f.write(convert_data_to_string(row))
            f.write("\n")
        f.write("\n")

        f.write("Class Features:")
        for row in class_features:
            if row != "\n":
                f.write(row)
                f.write("\n")
            for item in class_features[row]:
                if item != "\n":
                    f.write(item)
                    f.write("\n")
        f.write("\n")

        f.write("Class Archetypes:")
        f.write("\n")
        for i in range(len(class_archetypes)):
            f.write(archetype_names[i])
            f.write("\n")
            for row in class_archetypes[i]:
                f.write(row)
                f.write("\n")
                for item in class_archetypes[i][row]:
                    f.write(item)
                    f.write("\n")
        f.write("\n")

def write_quicklinks_to_file(quicklinks: dict):
    with open("quicklinks.txt", "w") as f:
        for link in quicklinks:
            if link != "\n" and link != "":
                f.write(link)
                f.write("\n")
            text = convert_data_to_string(quicklinks[link])
            if text != "\n" and text != "":
                f.write(text)
                f.write("\n")

        



    
def main():
    #get spell data
    #write_spells_to_file()

    #get class data
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_="feature")

    #returns a list of urls for the classes
    # class_url = get_class_url(results)
    
    # iteration = 0
    # for url in class_url:
    #     class_name = get_class_name(url)
    #     class_table_info = get_class_table_info(url)
    #     class_features = get_class_features(url)
        
    #     class_archetypes_url = get_class_archetypes(url)
    #     class_archetypes = []
    #     archetype_names = []
    #     for url in class_archetypes_url:
    #         archetype_names.append(get_class_name(url))
    #         class_archetypes.append(get_class_features(url))
    #     write_classes_to_file(class_name, class_table_info, class_features, archetype_names, class_archetypes, iteration)
    #     iteration += 1

    class_quicklinks = get_class_quicklinks(results)
    quicklinks_features = get_class_quicklink_features(class_quicklinks)
    write_quicklinks_to_file(quicklinks_features)


main()