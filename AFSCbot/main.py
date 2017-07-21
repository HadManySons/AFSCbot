import logging
import sys

from read_csv_files import get_AFSCs, get_afsc_links, get_prefixes
from setup_bot import open_pid, close_pid, login, setup_database
from process_comment import generate_reply, send_reply
from helper_functions import print_and_log

# 'AFSCbot' must be changed to 'airforce' for a production version of the script
#SUBREDDIT = 'airforce+airnationalguard'
SUBREDDIT = 'AFSCbot'


def main():
    # Initialize a logging object
    logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)
    print_and_log("Starting script")

    # reddit user object
    reddit = login()

    # creates file tracking if script is currently running
    open_pid()

    # setup pid, database, and AFSC dicts
    conn, dbCommentRecord = setup_database()

    # load all the AFSCs and prefixes into dictionaries
    try:
        full_afsc_dict = get_AFSCs()
        full_afsc_dict = get_afsc_links(reddit, full_afsc_dict)
        prefix_dict = get_prefixes()
        # subreddit instance of /r/AirForce.
        rAirForce = reddit.subreddit(SUBREDDIT)
    except Error as e:
        print_and_log("Couldn't load dicts, {}".format(e), error=True)
        close_pid()
        sys.exit(1)

    print_and_log("Starting processing loop for subreddit: " + SUBREDDIT)
    comments_seen = 0
    try:
        while True:
            # stream all comments from /r/AirForce
            for rAirForceComment in rAirForce.stream.comments():

                # prints a link to the comment. A True for permalink
                # generates a fast find (but is not an accurate link,
                # just makes the script faster (SIGNIFICANTLY FASTER)
                permlink = "http://www.reddit.com{}/".format(
                    rAirForceComment.permalink(True))
                print_and_log("Processing comment: " + permlink)

                # Pulls all comments previously commented on and checks
                # if the current comment has been replied to
                dbCommentRecord.execute(
                    "SELECT * FROM comments WHERE comment=?",
                    (rAirForceComment.id,))
                id_already_exists = dbCommentRecord.fetchone()

                # Make sure we don't reply to the same comment twice
                # or to the bot itself
                if id_already_exists:
                    print_and_log("Already replied to comment, skipping...")
                elif rAirForceComment.author in ("AFSCbot", "CSFAbot"):
                    print_and_log("Author was the bot, skipping...")
                else:
                    reply_text = generate_reply(rAirForceComment,
                                                    full_afsc_dict, prefix_dict)
                    if reply_text:
                        send_reply(reply_text, rAirForceComment)

                        # insert comment id into database so it wont be repeated
                        dbCommentRecord.execute('INSERT INTO comments VALUES (?);',
                                                (rAirForceComment.id,))
                        conn.commit()
                    else:
                        print("No AFSC found, skipping...")

                comments_seen += 1
                print()
                print("Comments processed since start of script: {}".format(
                        comments_seen))

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt")

    finally:
        conn.commit()
        conn.close()
        close_pid()


if __name__ == "__main__":
    main()
