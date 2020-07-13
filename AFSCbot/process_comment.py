import re

from helper_functions import print_and_log

ENLISTED_AFSC_REGEX = "(?:^|\s|[\,])(([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?))"
OFFICER_AFSC_REGEX = "(?:^|\s)(([A-Z]?)(\d\d[A-Z]([013579]|X?))([A-Z]?))"

ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                         'Craftsman', '', 'Superintendent']

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")

COMMENT_FOOTER = ("\n\n[^^Source](https://github.com/HadManySons/AFSCbot)"
                  " ^^| [^^Subreddit](https://www.reddit.com/r/AFSCbot/)")

def check_parents_for_matches(comment, match):
    """
    Checks parent comments for any previous matches of an
    AFSC, so the bot doesn't spam a comment thread
    :param comment: a PRAW instance of a comment
    :param match: a string containing an AFSC to check. "1A1X1" for example. Needs to be
    in uppercase
    :return: Returns true if a previous match was found, otherwise false if it
    reaches a top level comment without finding a match.
    """
    if comment.is_root:
        print_and_log("Is top level comment")
        return False
    else:
        formatted_parent_comment = comment.parent().body
        formatted_parent_comment = formatted_parent_comment.upper()
        if match in formatted_parent_comment:
            print_and_log("Previous match")
            return True
        else:
            print_and_log("Checking next parent")
            return check_parents_for_matches(comment.parent(), match)

def generate_reply(comment, full_afsc_dict, prefix_dict):
    """
    Generates a reply to a given comment based on any AFSC mentioned.
    :param comment: string body of comment to be replied to 
    :param full_afsc_dict: dict used for afsc lookups
    :param prefix_dict: dict used for prefix lookups
    :return: a list of strings representing lines that will be in the reply
    """

    formatted_comment = filter_out_quotes(comment.body)

    # Search through the comments for things that look like enlisted AFSCs
    matched_comments_enlisted = get_enlisted_regex_matches(formatted_comment)
    matched_comments_officer = get_officer_regex_matches(formatted_comment)

    # prepare dicts for enlisted and officer AFSCs
    enlisted_afsc_dict = full_afsc_dict["enlisted"]
    enlisted_prefix_dict = prefix_dict["enlisted"]
    officer_afsc_dict = full_afsc_dict["officer"]
    officer_prefix_dict = prefix_dict["officer"]

    comment_text = []

    # process all enlisted
    for match in matched_comments_enlisted:
        if check_parents_for_matches(comment, match.group(1).upper()):
            continue
        comment_text = process_comment(comment_text, match,
                                        enlisted_afsc_dict, enlisted_prefix_dict)

    # process all officer
    for match in matched_comments_officer:
        if check_parents_for_matches(comment, match.group(1).upper()):
            continue
        comment_text = process_comment(comment_text, match,
                                       officer_afsc_dict, officer_prefix_dict)

    return comment_text


def get_enlisted_regex_matches(formatted_comment):
    """
    Gets a regex match for enlisted AFSCs. 
    Note: Enlisted matching is NOT case sensitive.
    :param formatted_comment: string not including any quoted text
    :return: regex matches
    """
    enlisted_AFSC_search = re.compile(ENLISTED_AFSC_REGEX, re.IGNORECASE)
    matched_comments_enlisted = enlisted_AFSC_search.finditer(formatted_comment)
    return matched_comments_enlisted


def get_officer_regex_matches(formatted_comment):
    """
    Gets a regex match for officer AFSCs. 
    Note: Officer matching IS case sensitive.
    :param formatted_comment: string not including any quoted text
    :return: regex matches
    """
    # officer afsc matching is case sensitive to prevent 12s
    # from matching 12S and other officer AFSCs
    officer_AFSC_search = re.compile(OFFICER_AFSC_REGEX)
    matched_comments_officer = officer_AFSC_search.finditer(formatted_comment)
    return matched_comments_officer


def send_reply(comment_text, rAirForceComment):
    """
    Replies to rAirForceComment with comment_text using Bot that is 
    currently logged in.
    :param comment_text: list of strings representing lines in the reply
    :param rAirForceComment: reddit comment to be replied to
    """
    print_and_log("comment: {}".format(comment_text))

    comment_str = "\n\n".join(comment_text)
    rAirForceComment.reply(COMMENT_HEADER + comment_str + COMMENT_FOOTER)

    print_and_log("Sent reply...")


def filter_out_quotes(comment):
    """
    Removes any quoted text from reddit comment text. On reddit, lines of 
    quoted text begin with \n\n>. Single \n dont register as new line 
    in regards to quotes.
    :param comment_text: string of comment
    :return:
    """
    lines = comment.split("\n\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith(">"):
            lines.pop(i)
        else:
            i += 1
    return "\n\n".join(lines)


def process_comment(comment_text, match, afsc_dict, prefix_dict):
    """
    Takes the given enlisted AFSC match and appends a line of reply 
    to comment_text. If there is a wiki page it will also reply with that. If 
    there are no matches to AFSC dict then there is no change to comment_text.
    :param comment_text: list of strings representing lines in the reply
    :param match: regex match of enlisted AFSC
    :param afsc_dict: dict used for AFSC lookup
    :param prefix_dict: dict used for prefix lookup
    :return: modified comment_text with 0, 1, or 2 appended
    """

    whole_match = match.group(1).upper()
    prefix = match.group(2).upper()
    afsc = match.group(3).upper()
    skill_level = match.group(4).upper()
    suffix = match.group(5).upper()

    dict_type = afsc_dict["dict_type"]

    #print("Whole match: " + whole_match)
    if prefix:
        print("Prefix: " + prefix)
    print("AFSC: " + afsc)
    if skill_level:
        print("Skill Level: " + skill_level)
    if suffix:
        print("Suffix: " + suffix)

    # handle skill levels
    if dict_type == "enlisted":
        if skill_level != "0":
            # replaces the skill level with an X
            tempAFSC = afsc[:3] + "X" + afsc[4:]
        else:
            tempAFSC = afsc
    else:
        # standardize officer tempAFSC to be 12SX
        if skill_level == "X":
            tempAFSC = afsc
        elif skill_level.isnumeric():
            afsc = afsc[:-1] + "X"  # skill level printed as X
            tempAFSC = afsc[:-1] + "X"
        else:
            tempAFSC = afsc + 'X'

    comment_line = ""
    # if comment base AFSC is in dict of base AFSC's
    if tempAFSC in afsc_dict.keys():
        print_and_log("from whole_match: {}, found {} in {} AFSCs"
                      .format(whole_match, tempAFSC, dict_type))

        # build whole AFSC only if prefix and suffix exist
        if prefix in prefix_dict.keys():
            comment_line += prefix
        comment_line += afsc
        if suffix in afsc_dict[tempAFSC]["shreds"].keys():
            comment_line += suffix
        comment_line += " = "

        # Is there a prefix? If so, add its title
        if prefix:
            if prefix in prefix_dict.keys():
                comment_line += prefix_dict[prefix] + " "
                print_and_log("found prefix {} in {} dict"
                              .format(prefix, dict_type))
            else:
                print_and_log("could not find prefix {} in {} dict"
                              .format(prefix, dict_type))

        # add job title
        comment_line += afsc_dict[tempAFSC]["job_title"]

        # add skill level, officer skill level is ignored
        if dict_type == "enlisted":
            # if skill level given is not X or O, describe skill level given
            if skill_level != 'X' and skill_level != '0':
                comment_line += " " + \
                ENLISTED_SKILL_LEVELS[int(skill_level) - 1]

        # Is there a suffix? If so, add its title
        if suffix:
            if suffix in afsc_dict[tempAFSC]["shreds"].keys():
                comment_line += ", " + afsc_dict[tempAFSC]["shreds"][suffix]
                print_and_log("found suffix {} under {}"
                          .format(suffix, tempAFSC))
            else:
                print_and_log("could not find suffix {} under {}"
                              .format(suffix, tempAFSC))

        # Is there a link? If so, add its link
        afsc_link = afsc_dict[tempAFSC]["link"]
        if afsc_link:
            comment_line += " [^wiki]({})".format(afsc_link)
            print_and_log("found a link for {} at {}"
                          .format(tempAFSC, afsc_link))

        if comment_line not in comment_text:
            comment_text.append(comment_line)
    else:
        print_and_log("Did not find {} in {} AFSCs".format(tempAFSC, dict_type))
    print_and_log("-------")
    return comment_text


def break_up_regex(matches):
    """
    Creates a dict of regex matches for testing purposes.
    :param match: regex match of either enlisted or officer AFSC 
    :return: dict mapping an identifier string to the correct regex group
    """
    new_match = []
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
        new_match.append(match_dict)
    return new_match


if __name__ == "__main__":
    """Run this module directly to run unit tests"""
    import test_process_comment
