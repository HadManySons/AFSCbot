import re
import os

from helper_functions import print_and_log

# old regex, incase we need
#ENLISTED_AFSC_REGEX = "([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?)"
#OFFICER_AFSC_REGEX = "([A-Z]?)(\d\d[A-Z](X?))([A-Z]?)"

ENLISTED_AFSC_REGEX = "(?:^|\s|[\,])(([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?))"
OFFICER_AFSC_REGEX = "(?:^|\s)(([A-Z]?)(\d\d[A-Z]([013579]|X?))([A-Z]?))"

ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                         'Craftsman', '', 'Superintendent']

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")


def generate_reply(rAirForceComment, full_afsc_dict, prefix_dict):

    formatted_comment = rAirForceComment.body

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
    # enlisted afsc are not case-sensitive
    enlisted_AFSC_search = re.compile(ENLISTED_AFSC_REGEX, re.IGNORECASE)
    matched_comments_enlisted = enlisted_AFSC_search.finditer(formatted_comment)
    return matched_comments_enlisted


def get_officer_regex_matches(formatted_comment):
    # officer afsc are case-sensitive
    officer_AFSC_search = re.compile(OFFICER_AFSC_REGEX)
    matched_comments_officer = officer_AFSC_search.finditer(formatted_comment)
    return matched_comments_officer


def send_reply(comment_text, rAirForceComment):
    print_and_log("comment: {}".format(comment_text))
    comment_str = "\n\n".join(comment_text)
    rAirForceComment.reply(COMMENT_HEADER + comment_str)

    print_and_log("Sent reply...")


def process_enlisted(comment_text, enlisted_individual_matches, matchList,
                     enlisted_dict, prefix_dict):

    whole_match = enlisted_individual_matches.group(1).upper()
    prefix = enlisted_individual_matches.group(2).upper()
    afsc = enlisted_individual_matches.group(3).upper()
    skill_level = enlisted_individual_matches.group(4).upper()
    suffix = enlisted_individual_matches.group(5).upper()

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

        try:
            afsc_link = enlisted_dict[tempAFSC]["link"]
            comment_line += "\n\n Look they have a [Wiki Page]({})"\
                .format(afsc_link)
            print_and_log("found a link for {} at {}"
                          .format(tempAFSC, afsc_link))
        except KeyError:
            pass

        if comment_line not in comment_text:
            comment_text.append(comment_line)
    else:
        print_and_log("Did not find {} in enlisted AFSCs".format(tempAFSC))
    print("-------")
    return comment_text


def process_officer(comment_text, officer_individual_matches, matchList,
                    officer_dict, prefix_dict):

    whole_match = officer_individual_matches.group(1)
    prefix = officer_individual_matches.group(2)
    afsc = officer_individual_matches.group(3)
    skill_level = officer_individual_matches.group(4)
    suffix = officer_individual_matches.group(5)

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
        whole_match = match.group(1)
        prefix = match.group(2)
        afsc = match.group(3)
        skill_level = match.group(4)
        suffix = match.group(5)
        match_dict = {
                      "whole_match": whole_match.upper(),
                      "prefix": prefix.upper(),
                      "afsc": afsc.upper(),
                      "skill_level": skill_level.upper(),
                      "suffix": suffix.upper(),
                      }
        new_matches.append(match_dict)
    return new_matches


if __name__ == "__main__":
    """Run this module directly to run unit tests"""
    import test_process_comment
