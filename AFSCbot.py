import logging

import os
import sys

from read_csv_files import get_AFSCs, get_AFSC_links, get_prefixes
from setup_bot import open_pid, login, setup_database
from process_comment import process_comment
from helper_functions import print_and_log

# 'AFSCbot' must be changed to 'airforce' for a production version of the script
#SUBREDDIT = 'airforce+airnationalguard'
SUBREDDIT = 'AFSCbot'

PID_FILE = "AFSCbot.pid"


def main():
    # Initialize a logging object
    logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)
    print_and_log("Starting script")

    # reddit user object
    reddit = login()

    # creates file tracking if script is currently running
    open_pid(PID_FILE)

    # setup pid, database, and AFSC dicts
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


if __name__ == "__main__":
    main()
