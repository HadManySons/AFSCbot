import re
import unittest

from helper_functions import print_and_log

# regex for locating AFSCs
ENLISTED_AFSC_REGEX = "([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?)"
OFFICER_AFSC_REGEX = "([A-Z]?)(\d\d[A-Z](X?))([A-Z]?)"
ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                       'Craftsman', '', 'Superintendent']

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")


def generate_reply(rAirForceComment, dbCommentRecord,
                    full_afsc_dict, prefix_dict):

    # prints a link to the comment. A True for permalink
    # generates a fast find (but is not an accurate link,
    # just makes the script faster (SIGNIFICANTLY FASTER)
    permlink = "http://www.reddit.com{}/".format(
                rAirForceComment.permalink(True))

    print_and_log("Processing comment: " + permlink)

    # Pulls all comments previously commented on
    dbCommentRecord.execute("SELECT * FROM comments WHERE comment=?",
                            (rAirForceComment.id,))

    id_exists = dbCommentRecord.fetchone()

    # Keep a list of matched AFSCs so they're only posted once
    match_list = []
    comment_text = ""

    # Make sure we don't reply to the same comment twice
    # or to the bot itself
    if id_exists:
        print("Already processed comment: {}, skipping".format(
                rAirForceComment.id))
    elif rAirForceComment.author == "AFSCbot":
        print("Author was the bot, skipping...")
    else:
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

        for enlisted_individual_matches in matched_comments_enlisted:
            comment_text = process_enlisted(comment_text, enlisted_individual_matches,
                                           match_list, enlisted_dict, prefix_dict)

        for officer_individual_matches in matched_comments_officer:
            comment_text = process_officer(comment_text, officer_individual_matches,
                                          match_list, officer_dict, prefix_dict)
    return comment_text, match_list


def send_reply(comment_text, match_list, rAirForceComment, dbCommentRecord, conn):
    comment_info_text = ("Commenting on AFSC: {} by: {}. Comment ID: {}".format(
                        match_list, rAirForceComment.author, rAirForceComment.id))
    print_and_log(comment_info_text)

    rAirForceComment.reply(COMMENT_HEADER + comment_text)

    dbCommentRecord.execute('INSERT INTO comments VALUES (?);',
                            (rAirForceComment.id,))
    conn.commit()


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


def process_officer(comment_text, officer_individual_matches,matchList,
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

    if whole_match in matchList:
        return comment_text

    tempAFSC = afsc
    print("Pre temp: " + tempAFSC)
    if not skill_level:
        tempAFSC = tempAFSC + 'X'
        print("Post temp: " + tempAFSC)

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


class ProcessCommentTest(unittest.TestCase):
    def test_normal_afsc_with_num(self):
        comment = "some comment"

        expected_reply = "some string"
        actual_reply = process_comment(comment, conn, dbCommentRecord,
                        full_afsc_dict, prefix_dict)
        self.assertEqual(expected_reply, actual_reply)