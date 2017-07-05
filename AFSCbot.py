import logging
import time
import os
import sys
import re

from read_csv_files import get_AFSCs, get_AFSC_links, get_prefixes
from setup_bot import open_pid, login, setup_database


LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "

# 'AFSCbot' must be changed to 'airforce' for a production version of the script
#SUBREDDIT = 'airforce+airnationalguard'
SUBREDDIT = 'AFSCbot'

# regex for locating AFSCs
ENLISTED_AFSC_REGEX = "([A-Z]?)(\d[A-Z]\d([013579]|X)\d)([A-Z]?)"
OFFICER_AFSC_REGEX = "([A-Z]?)(\d\d[A-Z](X?))([A-Z]?)"
ENLISTED_SKILL_LEVELS = ['Helper', '', 'Apprentice', '', 'Journeyman', '',
                       'Craftsman', '', 'Superintendent']

ENLISTED_PREFIXES = {"K": "Instructor",
                     "Q": "Evaluator",
                     "T": "Instructor",
                     "W": "Weapons Officer"}

OFFICER_PREFIXES = {"K": "Instructor",
                    "Q": "Evaluator",
                    "T": "Instructor",
                    "W": "Weapons Officer"}

COMMENT_HEADER = ("^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the"
                  " ^^associated ^^job ^^title:\n\n")


def main():

    # Initialize a logging object
    logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)
    print_and_log("Starting script")

    # reddit user object
    reddit = login()

    # setup pid, database, and AFSC dicts
    open_pid()
    conn, dbCommentRecord = setup_database()

    # load all the AFSCs, prefixes and shreds into lists
    full_afsc_dict = get_AFSCs()
    prefix_dict = get_prefixes()
    AFSC_links = get_AFSC_links(reddit)

    # subreddit instance of /r/AirForce.
    rAirForce = reddit.subreddit(SUBREDDIT)

    print_and_log("Starting processing loop for subreddit: " + SUBREDDIT)
    comments_seen = 0
    try:
        while True:
            try:
                # stream all comments from /r/AirForce
                for rAirForceComment in rAirForce.stream.comments():
                    process_comment(rAirForceComment, conn, dbCommentRecord,
                                    full_afsc_dict, prefix_dict)
                    comments_seen += 1
                    print()
                    print("Comments processed since start of script: {}".format(
                            comments_seen))

            # what to do if Ctrl-C is pressed while script is running
            except KeyboardInterrupt:
                print_and_log("Exiting due to keyboard interrupt",
                              error=True)
                sys.exit(0)

            except KeyError:
                print_and_log("AFSC not found in the dictionary, but "
                              "the dict was called for some reason",
                              error=True)

            # is this necessary? shouldn't program just crash
            # otherwise we can cover specific errors related to connection
            # makes debugging harder without printing full exception info
            #except Exception as err:
            #    print_and_log("Unhandled Exception: " + str(err),
            #                  error=True)

            finally:
                conn.commit()
    finally:
        conn.commit()
        conn.close()
        os.unlink(PID_FILE)


def process_comment(rAirForceComment, conn, dbCommentRecord,
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

        # Keep a list of matched AFSCs so they're only posted once
        matchList = []
        commentText = ""

        enlisted_dict = full_afsc_dict["enlisted"]
        officer_dict = full_afsc_dict["officer"]

        for enlisted_individual_matches in matched_comments_enlisted:
            commentText = process_enlisted(commentText, enlisted_individual_matches,
                                           matchList, enlisted_dict, prefix_dict)

        for officer_individual_matches in matched_comments_officer:
            commentText = process_officer(commentText, officer_individual_matches,
                                          matchList, officer_dict, prefix_dict)

        # if commentText is not empty, build reply
        if commentText != "":
            comment_info_text = ("Commenting on AFSC: {} by:"
                                 " {}. Comment ID: {}".format(
                                matchList, rAirForceComment.author,
                                rAirForceComment.id))
            print_and_log(comment_info_text)


            rAirForceComment.reply(COMMENT_HEADER + commentText)

            dbCommentRecord.execute('INSERT INTO comments VALUES (?);',
                                    (rAirForceComment.id,))
            conn.commit()


def process_enlisted(commentText, enlisted_individual_matches, matchList,
                     enlisted_dict, prefix_dict):

    whole_match = enlisted_individual_matches.group(0)
    prefix = enlisted_individual_matches.group(1)
    afsc = enlisted_individual_matches.group(2)
    skill_level = enlisted_individual_matches.group(3)
    suffix = enlisted_individual_matches.group(4)

    if whole_match in matchList:
        return commentText

    #replaces the skill level with an X
    tempAFSC = list(afsc)
    tempAFSC[3] = 'X'
    tempAFSC = "".join(tempAFSC)

    # if comment base AFSC is in dict of base AFSC's
    for base_afsc in enlisted_dict:
        if base_afsc == tempAFSC:
            matchList.append(whole_match)
            commentText += whole_match + " = "

            # Is there a prefix? If so, add it
            if prefix and prefix in prefix_dict["enlisted"].keys():
                commentText += prefix_dict["enlisted"][prefix] + " "

            # add job title
            commentText += enlisted_dict[base_afsc]["job_title"]

            # if skill level given is not X or O, describe skill level given
            if skill_level != 'X' and skill_level != '0':
                commentText += " " + \
                ENLISTED_SKILL_LEVELS[int(skill_level) - 1]

            # Is there a suffix? If so, add it
            if suffix and suffix == enlisted_dict[base_afsc]["shred"]["char"]:
                commentText += ", " + enlisted_dict[base_afsc]["shred"]["title"]

            commentText += "\n\n"
    return commentText


def process_officer(commentText, officer_individual_matches,matchList,
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
        return commentText

    tempAFSC = afsc
    print("Pre temp: " + tempAFSC)
    if not skill_level:
        tempAFSC = tempAFSC + 'X'
        print("Post temp: " + tempAFSC)

    #################################
    for base_afsc in officer_dict:
        if tempAFSC in officer_base_AFSC_list[i]:
            matchList.append(whole_match)
            commentText += whole_match + " = "

            if prefix:
                for j in range(len(officer_prefix_list)):
                    if prefix == officer_prefix_list[j]:
                        commentText += officer_prefix_title[j] + " "
            commentText += officer_base_AFSC_jt[i]

            if suffix:
                for j in range(len(officer_shred_list)):
                    if (tempAFSC == officer_shred_AFSC[j]
                            and suffix == officer_shred_list[j]):
                        print(officer_shred_title[j])
                        commentText += ", " + officer_shred_title[j]

            commentText += "\n\n"
    return commentText


def print_and_log(text, error=False):
    print(text)
    if error:
        logging.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logging.info(time.strftime(LOG_TIME_FORMAT) + text)


if __name__ == "__main__":
    main()
