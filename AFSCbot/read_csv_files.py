import csv
import os
from bs4 import BeautifulSoup
from helper_functions import has_number
from pprint import pprint

CSV_FOLDER = os.getcwd() + "/csv_files/"


def get_AFSCs(reddit):
    """
    Returns a dict used to lookup AFSCs
    full_afsc_dict -> "enlisted": -> 
                                     "1W0X1": -> "base_afsc": "1W0X1"
                                              -> "job_title": "Weather Technician"
                                              -> "shreds": {}
                                              -> "link": "https://www.reddit.com/r/AirForce/wiki/jobs/1w0x1"
                                     ...
                   -> "officer": ->
                                     "12SX":  -> "base_afsc": "12SX"
                                              -> "job_title": "Special Operations Combat Systems Officer"
                                              -> "shreds": ->
                                                              "C": "AC-130H"
                                                              "K": "MC-130H EWO"
                                                              ...
                                              -> "link": ""
                                     ...
    :param reddit: PRAW reddit object
    :return: full_afsc_dict used for looking up AFSC information
    """
    enlisted_dict = {"dict_type": "enlisted"}
    officer_dict = {"dict_type": "officer"}
    full_afsc_dict = {"enlisted": enlisted_dict,
                      "officer": officer_dict}

    # add AFSCs and their titles
    add_afsc(enlisted_dict, "EnlistedAFSCs.csv")
    add_afsc(officer_dict, "OfficerAFSCs.csv")

    # add shreds to AFSCs
    add_shreds(enlisted_dict, "EnlistedShreds.csv")
    add_shreds(officer_dict, "OfficerShreds.csv")

    # add links to AFSCs
    add_afsc_links(full_afsc_dict, reddit)

    # uncomment to see full dictionary
    #pprint(full_afsc_dict)

    return full_afsc_dict


def get_prefixes():
    """
    Returns a dict used to lookup prefixes.
    prefix_dict -> "enlisted" -> 
                                   "K": "Instructor"
                                   "Q": "Evaluator"
                                   ...
                -> "officer" ->    
                                   "S": "Safety"
                                   "W": "Weapons Officer"
                                   ...
    :return: prefix_dict
    """
    prefix_enlisted = {}
    prefix_officer = {}

    prefix_dict = {"enlisted": prefix_enlisted,
                   "officer": prefix_officer}

    # add prefixes
    add_prefix(prefix_enlisted, "EnlistedPrefixes.csv")
    add_prefix(prefix_officer, "OfficerPrefixes.csv")

    return prefix_dict


def add_prefix(dict, fname):
    """
    Add prefixes from given filename into the dictionary.
    :param dict: empty dict
    :param fname: CSV file using '#' as delimiter
    """
    with open(CSV_FOLDER + fname, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            prefix_char = row[0]
            prefix_title = row[1]
            dict[prefix_char] = prefix_title


def add_afsc(dict, fname):
    """
    Add AFSCs from given filename into the dictionary.
    :param dict: empty dictionary
    :param fname: CSV file using '#' as delimiter
    """
    with open(CSV_FOLDER + fname, newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            base_afsc = row[0]
            job_title = row[1]
            afsc_dict = {"base_afsc": base_afsc,
                         "job_title": job_title,
                         "shreds": {},
                         "link": ""}
            dict[base_afsc] = afsc_dict


def add_shreds(afsc_dict, fname):
    """
    Add shreds from given filename into the dictionary.
    :param dict: either enlisted_dict or officer_dict
    :param fname: CSV file using '#' as delimiter
    """
    with open(CSV_FOLDER + fname, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            base_afsc = row[0]
            shred_char = row[1]
            shred_title = row[2]
            # if shred AFSC not in base afsc, skip it
            try:
                afsc_dict[base_afsc]["shreds"][shred_char] = shred_title
            except KeyError:
                pass


def add_afsc_links(full_afsc_dict, reddit):
    """
    Add links to /r/AirForce wiki from given filename into the dictionary.
    :param dict: either enlisted_dict or officer_dict
    :param reddit: PRAW reddit object
    """
    # gets dict of AFSC to link on /r/AirForce wiki
    wiki_page = reddit.subreddit("AirForce").wiki["index"]
    wiki_soup = BeautifulSoup(wiki_page.content_html, "html.parser")
    links = wiki_soup.find_all("a")

    # currently all wiki AFSC are enlisted
    for link in links:
        # not all links have /r/AirForce/wiki/jobs so this is more generalized
        # using only /r/AirForce/ wiki links
        if "www.reddit.com/r/AirForce/wiki/" in link["href"]:
            AFSC_code = link["href"].split("/")[-1].upper()
            base_afsc = AFSC_code[:5]  # shaves off any prefixes
            if base_afsc in full_afsc_dict["enlisted"].keys():
                full_afsc_dict["enlisted"][base_afsc]["link"] = link["href"]
