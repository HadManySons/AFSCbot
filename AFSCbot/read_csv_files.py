import csv
import os
from bs4 import BeautifulSoup
from helper_functions import has_number
from pprint import pprint

CSV_FOLDER = os.getcwd() + "\csv_files\\"


def get_AFSCs():
    enlisted_dict = {"dict_type": "enlisted"}
    officer_dict = {"dict_type": "officer"}
    full_afsc_dict = {"enlisted": enlisted_dict,
                      "officer": officer_dict}

    # setup job titles
    with open(CSV_FOLDER + 'EnlistedAFSCs.csv', newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            base_afsc = row[0]
            job_title = row[1]
            afsc_dict = {"base_afsc": base_afsc,
                         "job_title": job_title,
                         "shreds": {}}
            enlisted_dict[base_afsc] = afsc_dict

    with open(CSV_FOLDER + 'OfficerAFSCs.csv', newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            base_afsc = row[0]
            job_title = row[1]
            afsc_dict = {"base_afsc": base_afsc,
                         "job_title": job_title,
                         "shreds": {}}
            officer_dict[base_afsc] = afsc_dict

    # setup shreds
    with open(CSV_FOLDER + 'EnlistedShreds.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            base_afsc = row[0]
            shred_char = row[1]
            shred_title = row[2]
            # if shred AFSC not in base afsc, skip it
            try:
                enlisted_dict[base_afsc]["shreds"][shred_char] = shred_title
            except KeyError:
                pass

    with open(CSV_FOLDER + 'OfficerShreds.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            base_afsc = row[0]
            shred_char = row[1]
            shred_title = row[2]
            # if shred AFSC not in base afsc, skip it
            try:
                officer_dict[base_afsc]["shreds"][shred_char] = shred_title
            except KeyError:
                pass

    # uncomment to see full dictionary
    #pprint(full_afsc_dict)

    return full_afsc_dict


def get_prefixes():
    prefix_dict = {"enlisted": {},
                   "officer": {}}
    with open(CSV_FOLDER + 'EnlistedPrefixes.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            prefix_char = row[0]
            prefix_title = row[1]
            prefix_dict["enlisted"][prefix_char] = prefix_title

    with open(CSV_FOLDER + 'OfficerPrefixes.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            prefix_char = row[0]
            prefix_title = row[1]
            prefix_dict["officer"][prefix_char] = prefix_title
    return prefix_dict


def get_afsc_links(reddit, full_afsc_dict):
    # gets dict of AFSC to link on /r/AirForce wiki
    wiki_page = reddit.subreddit("AirForce").wiki["index"]
    wiki_soup = BeautifulSoup(wiki_page.content_html, "html.parser")
    links = wiki_soup.find_all("a")

    for link in links:
        # not all links have /r/AirForce/wiki/jobs so this is more generalized
        # using only /r/AirForce/ wiki links
        if "www.reddit.com/r/AirForce/wiki/" in link["href"]:
            AFSC_code = link["href"].split("/")[-1].upper()
            base_afsc = AFSC_code[:5]
            if base_afsc in full_afsc_dict["enlisted"].keys():
                full_afsc_dict["enlisted"][base_afsc]["link"] = link["href"]
    return full_afsc_dict