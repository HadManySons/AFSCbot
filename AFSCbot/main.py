import logging
import sys
import os
import time
from read_csv_files import get_AFSCs, get_prefixes
from setup_bot import login
from process_comment import generate_reply, send_reply
from helper_functions import print_and_log

credsPassword = os.environ.get('AFS_PASSWORD')
credsUserName = os.environ.get('AFS_USERNAME')
credsClientSecret = os.environ.get('AFS_SECRET')
credsClientID = os.environ.get("AFS_ID")
credsUserAgent = os.environ.get("AFS_USERAGENT")
subreddit = os.environ.get("AFS_SUBREDDIT")

#SUBREDDIT = 'airforce+airnationalguard+afrotc+airforcerecruits'
#SUBREDDIT = 'AFSCbot'

logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)

print_and_log(subreddit)

def checkForReplies(comment_list, rAirForceComments, permlink):
    """
    Checks any replies the comment in question to see if the bot
    has already replied
    :param comment_list: a list of comments that are replies
    :param rAirForceComments: the comment in question
    :param permlink: permanent link to the comment
    :return: returns true if the comment has already been replied to, otherwise false
    """
    for comment in comment_list:
        if rAirForceComments.id in comment.body:
            print_and_log("Already processed comment: " + permlink + ", skipping")
            print("Comment already processed, skipping")
            return True
    return False

def main():
    # Initialize a logging object
    #logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)
    print_and_log("Starting script")

    # reddit user object
    reddit = login(credsUserName, credsPassword, credsClientSecret, credsClientID, credsUserAgent)

    # load all the AFSCs and prefixes into dictionaries
    try:
        full_afsc_dict = get_AFSCs(reddit)
        prefix_dict = get_prefixes()
        # subreddit instance of /r/AirForce.
        rAirForce = reddit.subreddit(subreddit)
    except Exception as e:
        print_and_log("Couldn't load dicts, {}".format(e), error=True)
        sys.exit(1)

    print_and_log("Starting processing loop for subreddit: " + subreddit)
    comments_seen = 0
    try:
        while True:
            # stream all comments from /r/AirForce
            for rAirForceComment in rAirForce.stream.comments():

                #If the post is older than about 5 months, ignore it and move on.
                if (time.time() - rAirForceComment.created) > 13148715:
                    print_and_log("Post too old, continuing")
                    continue
                
                # prints a link to the comment. A True for permalink
                # generates a fast find (but is not an accurate link,
                # just makes the script faster (SIGNIFICANTLY FASTER)
                permlink = "http://www.reddit.com{}".format(
                    rAirForceComment.permalink)
                print_and_log("Processing comment: " + permlink)

                # Check replies to make sure the bot hasn't responded yet
                rAirForceComment.refresh()
                rAirForceComment.replies.replace_more()
                if checkForReplies(rAirForceComment.replies.list(), rAirForceComment, permlink):
                    continue

                reply_text = generate_reply(rAirForceComment,
                                                full_afsc_dict, prefix_dict)

                # log that comment was prepared
                comment_info_text = (
                "Preparing to reply to id {} by author: {}".format(
                    rAirForceComment.id, rAirForceComment.author))
                print_and_log(comment_info_text)

                if reply_text:
                    send_reply(reply_text, rAirForceComment)

                else:
                    print_and_log("No AFSC found, skipping...")

                comments_seen += 1
                print_and_log("")
                print_and_log("Comments processed since start of script: {}".format(
                        comments_seen))

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print_and_log("Exiting due to keyboard interrupt")

if __name__ == "__main__":
    main()
