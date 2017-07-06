import csv
import os
from bs4 import BeautifulSoup
from pprint import pprint

CSV_FOLDER = os.getcwd() + "\csv_files\\"
print(CSV_FOLDER + 'EnlistedAFSCs.csv')


def get_AFSCs():
    enlisted_dict = {}
    officer_dict = {}
    full_afsc_dict = {"enlisted": enlisted_dict,
                      "officer": officer_dict}

    # setup job titles
    with open(CSV_FOLDER + 'EnlistedAFSCs.csv', newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            base_afsc = row[0]
            job_title = row[1]
            afsc_dict = {"base_afsc": base_afsc,
                         "job_title": job_title}
            enlisted_dict[base_afsc] = afsc_dict

    with open(CSV_FOLDER + 'OfficerAFSCs.csv', newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            base_afsc = row[0]
            job_title = row[1]
            afsc_dict = {"base_afsc": base_afsc,
                         "job_title": job_title}
            officer_dict[base_afsc] = afsc_dict

    # setup shreds
    with open(CSV_FOLDER + 'EnlistedShreds.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            base_afsc = row[0]
            shred_char = row[1]
            shred_title = row[2]
            shred_dict = {"char": shred_char,
                          "title": shred_title}
            # if shred AFSC not in base afsc, skip it
            try:
                enlisted_dict[base_afsc]["shred"] = shred_dict
            except KeyError:
                pass

    with open(CSV_FOLDER + 'OfficerShreds.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            base_afsc = row[0]
            shred_char = row[1]
            shred_title = row[2]
            shred_dict = {"char": shred_char,
                          "title": shred_title}
            # if shred AFSC not in base afsc, skip it
            try:
                officer_dict[base_afsc]["shred"] = shred_dict
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


def get_AFSC_links(reddit):
    # gets dict of AFSC to link on /r/AirForce wiki
    wiki_page = reddit.subreddit("AirForce").wiki["index"]
    wiki_soup = BeautifulSoup(wiki_page.content_html, "html.parser")
    links = wiki_soup.find_all("a")

    AFSC_links = {}
    for link in links:
        # not all links have /r/AirForce/wiki/jobs so this is more generalized
        # using only /r/AirForce/wiki/
        if "www.reddit.com/r/AirForce/wiki/" in link["href"]:
            AFSC_code = link["href"].split("/")[-1]
            AFSC_links[AFSC_code] = link["href"]
    return AFSC_links