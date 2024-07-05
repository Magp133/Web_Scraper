import re

CROWD_CONTROL = ["charmed", "stunned", "frightened", "restrained", 
                 "pushed", "blinded", "deafened", "grappled", "incapacitated",
                   "paralyzed", "petrified", "prone", "unconscious", "exhaustion"]
HEALING = ["heal", "regrow", "restore", "revive" ]
DAMAGE = ["damage"]
HIT_POINTS = r"\d{1,2}d\d{1,3}"

SAVING_THROW = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

def process_strings(input_dictionary: dict):
    """"
    Search through the different patterns to find matches to add a tag to the object.
    The object is a dict and should have the key: Description.
    Add a new key called: Tags containing the tags for the spell. 
    These tages will be called the overall pattern name. e.g "Crowd Control"
    """

    spell_tags = list()

    cc_pattern = re.compile(r"(?=("+'|'.join(CROWD_CONTROL)+r"))")
    if re.findall(cc_pattern, input_dictionary["Description"]):
        spell_tags.append("Crowd Control")
        input_dictionary["Tags"] = spell_tags
        return input_dictionary
    
    heal_pattern = re.compile(r"(?=("+'|'.join(HEALING)+r"))")
    if re.findall(heal_pattern, input_dictionary["Description"]):
        spell_tags.append("Healing")
        input_dictionary["Tags"] = spell_tags
        return input_dictionary
    
    damage_pattern = re.compile(r"(?=("+'|'.join(DAMAGE)+r"))")
    if re.findall(damage_pattern, input_dictionary["Description"]):
        spell_tags.append("Damage")
        input_dictionary["Tags"] = spell_tags
        return input_dictionary
    
    saving_throw_pattern = re.compile(r"(?=("+'|'.join(SAVING_THROW)+r"))")
    saving_throw = re.findall(saving_throw_pattern, input_dictionary["Description"])
    if saving_throw:
        spell_tags.append("Saving Throw " + saving_throw[0])
        input_dictionary["Tags"] = spell_tags
        return input_dictionary

    return input_dictionary

def process_hitpoint_values(input_dictionary: dict):
    """
    Find the hitpoint changes via healing or damage within description.
    Record the change in hitpoints.
    Record the growth of the change as the spell/ player level changes.
    """


    hit_point_pattern = re.compile(HIT_POINTS)
    if "At Higher Levels." in input_dictionary:
        hit_point_values_higher_levels = re.findall(hit_point_pattern, input_dictionary["At Higher Levels."])
        input_dictionary["Hitdie Growth"] = hit_point_values_higher_levels
        
    hit_point_values_description = re.findall(hit_point_pattern, input_dictionary["Description"])
    if len(hit_point_values_description) > 0:
        input_dictionary["Hitdie"] = hit_point_values_description


    return input_dictionary


def check_if_ua(lineage_url: str):
    """
    Checks if the lineage is a ua version of a lineage.
    Check if the url ends in ua.
    """
    if lineage_url[-2:] == "ua":
        return True
    return False

def get_trait_names(trait_text: str):
    """
    Get the names of the traits for the lineage.
    """
    match = re.search(r"(.*?)\.", trait_text)

    return match.group(1), trait_text[match.end():]


def check_header(header: str, search_term: str):
    """
    Checks if the search term is in the header.
    """

    if search_term in header.lower():
        return True
    return False
