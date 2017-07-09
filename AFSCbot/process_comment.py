import re
import unittest

from helper_functions import print_and_log

# adjust regex to require whitespace on the outside, and punctuation on the right

# regex for locating AFSCs
ENLISTED_AFSC_REGEX = "([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?)"
OFFICER_AFSC_REGEX = "([A-Z]?)(\d\d[A-Z](X?))([A-Z]?)"

ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                         'Craftsman', '', 'Superintendent']

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")


def generate_reply(rAirForceComment, full_afsc_dict, prefix_dict):

    formatted_comment = rAirForceComment.body.upper()

    # Search through the comments for things that look like enlisted AFSCs
    matched_comments_enlisted = get_enlisted_regex_matches(formatted_comment)
    matched_comments_officer = get_officer_regex_matches(formatted_comment)

    # prepare dicts for enlisted and officer AFSCs
    enlisted_dict = full_afsc_dict["enlisted"]
    officer_dict = full_afsc_dict["officer"]

    match_list = []
    comment_text = []

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


def get_enlisted_regex_matches(formatted_comment):
    enlisted_AFSC_search = re.compile(ENLISTED_AFSC_REGEX, re.IGNORECASE)
    matched_comments_enlisted = enlisted_AFSC_search.finditer(formatted_comment)
    return matched_comments_enlisted


def get_officer_regex_matches(formatted_comment):
    officer_AFSC_search = re.compile(OFFICER_AFSC_REGEX, re.IGNORECASE)
    matched_comments_officer = officer_AFSC_search.finditer(formatted_comment)
    return matched_comments_officer


def send_reply(comment_text, rAirForceComment):
    print_and_log("comment: {}".format(comment_text))
    comment_str = "\n\n".join(comment_text)
    rAirForceComment.reply(COMMENT_HEADER + comment_str)

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

    print("Whole match: " + whole_match)
    if prefix:
        print("Prefix: " + prefix)
    print("AFSC: " + afsc)
    if skill_level:
        print("Skill Level: " + skill_level)
    if suffix:
        print("Suffix: " + suffix)

    # replaces the skill level with an X
    tempAFSC = list(afsc)
    tempAFSC[3] = 'X'
    tempAFSC = "".join(tempAFSC)

    comment_line = ""
    # if comment base AFSC is in dict of base AFSC's
    if tempAFSC in enlisted_dict.keys():
        print_and_log("from whole_match: {}, found {} in enlisted AFSCs"
                      .format(whole_match, tempAFSC))

        matchList.append(whole_match)
        comment_line += whole_match + " = "

        # Is there a prefix? If so, add it
        if prefix:
            if prefix in prefix_dict["enlisted"].keys():
                comment_line += prefix_dict["enlisted"][prefix] + " "
                print_and_log("found prefix {} in enlisted dict"
                              .format(prefix))
            else:
                print_and_log("could not fimd prefix {} in enlisted dict"
                              .format(prefix))

        # add job title
        comment_line += enlisted_dict[tempAFSC]["job_title"]

        # if skill level given is not X or O, describe skill level given
        if skill_level != 'X' and skill_level != '0':
            comment_line += " " + \
            ENLISTED_SKILL_LEVELS[int(skill_level) - 1]

        # Is there a suffix? If so, add it
        if suffix:
            if suffix in enlisted_dict[tempAFSC]["shreds"].keys():
                comment_line += ", " + enlisted_dict[tempAFSC]["shreds"][suffix]
                print_and_log("found suffix {} under {}"
                          .format(suffix, tempAFSC))
            else:
                print_and_log("could not find suffix {} under {}"
                              .format(suffix, tempAFSC))

        if comment_line not in comment_text:
            comment_text.append(comment_line)
    else:
        print_and_log("Did not find {} in enlisted AFSCs".format(tempAFSC))
    print("-------")
    return comment_text


def process_officer(comment_text, officer_individual_matches, matchList,
                    officer_dict, prefix_dict):

    whole_match = officer_individual_matches.group(0)
    prefix = officer_individual_matches.group(1)
    afsc = officer_individual_matches.group(2)
    skill_level = officer_individual_matches.group(3)
    suffix = officer_individual_matches.group(4)

    # if already commented, dont add it again
    if whole_match in matchList:
        return comment_text

    print("Whole match: " + whole_match)
    if prefix:
        print("Prefix: " + prefix)
    print("AFSC: " + afsc)
    if skill_level:
        print("Skill Level: " + skill_level)
    if suffix:
        print("Suffix: " + suffix)

    if skill_level:
        tempAFSC = afsc
    else:
        tempAFSC = afsc + 'X'

    comment_line = ""
    if tempAFSC in officer_dict.keys():
        print_and_log("from whole_match: {}, found {} in officer AFSCs"
                      .format(whole_match, tempAFSC))

        matchList.append(whole_match)
        comment_line += whole_match + " = "

        # Is there a prefix? If so, add it
        if prefix:
            if prefix in prefix_dict["officer"].keys():
                comment_line += prefix_dict["officer"][prefix] + " "
                print_and_log("found prefix {} in officer dict"
                              .format(prefix))
            else:
                print_and_log("could not fimd prefix {} in officer dict"
                              .format(prefix))

        # add job title
        comment_line += officer_dict[tempAFSC]["job_title"]

        # Is there a suffix? If so, add it
        if suffix:
            if suffix in officer_dict[tempAFSC]["shreds"].keys():
                comment_line += ", " + officer_dict[tempAFSC]["shreds"][suffix]
                print_and_log("found suffix {} under {}"
                              .format(suffix, tempAFSC))
            else:
                print_and_log("could not find suffix {} under {}"
                              .format(suffix, tempAFSC))

        if comment_line not in comment_text:
            comment_text.append(comment_line)
    else:
        print_and_log("Did not find {} in officer AFSCs".format(tempAFSC))
    print("-------")
    return comment_text


def break_up_regex(matches):
    new_matches = []
    for match in matches:
        whole_match = match.group(0)
        prefix = match.group(1)
        afsc = match.group(2)
        skill_level = match.group(3)
        suffix = match.group(4)
        match_dict = {
                      "whole_match": whole_match,
                      "prefix": prefix,
                      "afsc": afsc,
                      "skill_level": skill_level,
                      "suffix": suffix,
                      }
        new_matches.append(match_dict)
    return new_matches

#####################
""" Unit tests """
#####################

"""
bugs identified:
- afsc within other words still gets picked up "someletters1T0X1moreletters" 
    is this intended?
- afsc within hyperlink should not be matched
"""


class EnlistedRegexMatch(unittest.TestCase):
    def test_normal_afsc(self):
        comment = "1W051"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W051")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W051")
        self.assertEqual(str_matches[0]["skill_level"], "5")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_normal_prefix(self):
        comment = "K3E491"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "K3E491")
        self.assertEqual(str_matches[0]["prefix"], "K")
        self.assertEqual(str_matches[0]["afsc"], "3E491")
        self.assertEqual(str_matches[0]["skill_level"], "9")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_normal_suffix(self):
        comment = "2A334L"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "2A334L")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "2A334")
        self.assertEqual(str_matches[0]["skill_level"], "3")
        self.assertEqual(str_matches[0]["suffix"], "L")

    def test_normal_prefix_and_suffix(self):
        comment = "K3N1X1Q"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "K3N1X1Q")
        self.assertEqual(str_matches[0]["prefix"], "K")
        self.assertEqual(str_matches[0]["afsc"], "3N1X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "Q")

    def test_afsc_with_3_zeros(self):
        # should skill level return 0 or X or blank?
        comment = "9J000"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "9J000")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "9J000")
        self.assertEqual(str_matches[0]["skill_level"], "0")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "8P100"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "8P100")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "8P100")
        self.assertEqual(str_matches[0]["skill_level"], "0")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_block_of_text(self):
        comment = "here look at that 1C4X1 he is so cool"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1C4X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1C4X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_similar_to_afsc(self):
        comment = "1W0X"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "1W01"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "AW0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "1WOX1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

    def test_shred_is_number(self):
        comment = "1W0X12"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "1W0X123"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_prefix_is_number(self):
        comment = "11W0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "121W0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_afsc_within_other_words(self):
        comment = "someletters1T0X1moreletters"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)

        self.assertEqual(len(str_matches), 0)

    def test_afsc_with_punctuation(self):
        comment = "1S071."
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1S071")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1S071")
        self.assertEqual(str_matches[0]["skill_level"], "7")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "1S071,"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

        comment = "1S071?"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

        comment = "1S071,"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

    def test_afsc_in_hyperlink(self):
        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/1a8x1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/1a8x1/other"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

"""
Officer tests:
13S1E should pick up on 13S and shred E and ignore skill level, currently doesnt
"""

if __name__ == "__main__":
    unittest.main()