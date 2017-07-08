import re
import unittest

from helper_functions import print_and_log
from setup_bot import setup_database
from read_csv_files import get_AFSCs, get_prefixes

# regex for locating AFSCs
ENLISTED_AFSC_REGEX = "([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?)"
OFFICER_AFSC_REGEX = "([A-Z]?)(\d\d[A-Z](X?))([A-Z]?)"

ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                       'Craftsman', '', 'Superintendent']

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")


def generate_reply(rAirForceComment, full_afsc_dict, prefix_dict):

    # Keep a list of matched AFSCs so they're only posted once
    match_list = []
    comment_text = ""

    formattedComment = rAirForceComment.body.upper()

    # Search through the comments for things that look like enlisted AFSCs
    enlisted_AFSC_search = re.compile(ENLISTED_AFSC_REGEX, re.IGNORECASE)
    matched_comments_enlisted = enlisted_AFSC_search.finditer(
        formattedComment)

    officer_AFSC_search = re.compile(OFFICER_AFSC_REGEX, re.IGNORECASE)
    matched_comments_officer = officer_AFSC_search.finditer(
        formattedComment)

    enlisted_dict = full_afsc_dict["enlisted"]
    officer_dict = full_afsc_dict["officer"]

    """
    print("comment_text", comment_text)
    print(type(comment_text))
    for item in matched_comments_enlisted:
        print(item)
        print(type(item))
    print("match_list", match_list)
    print(type(match_list))
    """

    # process all enlisted
    for enlisted_individual_matches in matched_comments_enlisted:
        comment_text = process_enlisted(comment_text, enlisted_individual_matches,
                                       match_list, enlisted_dict, prefix_dict)

    # process all officer
    for officer_individual_matches in matched_comments_officer:
        comment_text = process_officer(comment_text, officer_individual_matches,
                                      match_list, officer_dict, prefix_dict)

    # log that comment was prepared
    comment_info_text = ("Preparing to reply: {} by: {}. Comment ID: {}".format(
        match_list, rAirForceComment.author, rAirForceComment.id))
    print_and_log(comment_info_text)

    return comment_text


def send_reply(comment_text, rAirForceComment):
    rAirForceComment.reply(COMMENT_HEADER + comment_text)
    print_and_log("Sent reply...")


def process_enlisted(comment_text, enlisted_individual_matches, matchList,
                     enlisted_dict, prefix_dict):

    whole_match = enlisted_individual_matches.group(0)
    prefix = enlisted_individual_matches.group(1)
    afsc = enlisted_individual_matches.group(2)
    skill_level = enlisted_individual_matches.group(3)
    suffix = enlisted_individual_matches.group(4)

    if whole_match in matchList:
        return comment_text

    # replaces the skill level with an X
    tempAFSC = list(afsc)
    tempAFSC[3] = 'X'
    tempAFSC = "".join(tempAFSC)

    # if comment base AFSC is in dict of base AFSC's
    for base_afsc in enlisted_dict:
        if base_afsc == tempAFSC:
            matchList.append(whole_match)
            comment_text += whole_match + " = "

            # Is there a prefix? If so, add it
            if prefix and prefix in prefix_dict["enlisted"].keys():
                comment_text += prefix_dict["enlisted"][prefix] + " "

            # add job title
            comment_text += enlisted_dict[base_afsc]["job_title"]

            # if skill level given is not X or O, describe skill level given
            if skill_level != 'X' and skill_level != '0':
                comment_text += " " + \
                ENLISTED_SKILL_LEVELS[int(skill_level) - 1]

            # Is there a suffix? If so, add it
            if suffix and suffix == enlisted_dict[base_afsc]["shred"]["char"]:
                comment_text += ", " + enlisted_dict[base_afsc]["shred"]["title"]

            comment_text += "\n\n"
    return comment_text


def process_officer(comment_text, officer_individual_matches, matchList,
                    officer_dict, prefix_dict):

    whole_match = officer_individual_matches.group(0)
    prefix = officer_individual_matches.group(1)
    afsc = officer_individual_matches.group(2)
    skill_level = officer_individual_matches.group(3)
    suffix = officer_individual_matches.group(4)

    print("Whole match: " + whole_match)
    if prefix:
        print("Prefix: " + prefix)
    print("AFSC: " + afsc)
    if skill_level:
        print("Skill Level: " + skill_level)
    if suffix:
        print("Suffix: " + suffix)
    print("-------")

    if whole_match in matchList:
        return comment_text

    tempAFSC = afsc
    if not skill_level:
        tempAFSC = tempAFSC + 'X'

    for base_afsc in officer_dict:
        if base_afsc == tempAFSC:
            matchList.append(whole_match)
            comment_text += whole_match + " = "

            # Is there a prefix? If so, add it
            if prefix and prefix in prefix_dict["officer"].keys():
                comment_text += prefix_dict["officer"][prefix] + " "

            # add job title
            comment_text += officer_dict[base_afsc]["job_title"]

            # Is there a suffix? If so, add it
            if suffix and suffix == officer_dict[base_afsc]["shred"]["char"]:
                comment_text += ", " + officer_dict[base_afsc]["shred"]["title"]

            comment_text += "\n\n"
    return comment_text


class ProcessEnlistedTest(unittest.TestCase):
    def test_officer_something(self):
        comment_text = "" # it will be empty if no enlisted found
        officer_individual_matches = "????"
        matchList = "????"
        officer_dict = get_AFSCs()["officer"]
        prefix_dict = get_prefixes()

        expected_reply = "some string"
        actual_reply = process_officer(comment_text, officer_individual_matches, matchList,
                    officer_dict, prefix_dict)
        self.assertEqual(expected_reply, actual_reply)

if __name__ == "__main__":
    unittest.main()