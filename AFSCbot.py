from pathlib import Path
import logging
import time
import os
import sys
import csv
import praw
import sqlite3

PID_FILE = "AFSCbot.pid"
CRED_FILE = 'AFSCbotCreds.txt'
DB_FILE = "AFSCbotCommentRecord.db"
AFSC_FILE = 'AFSClist.csv'
LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "

# 'AFSCbot' must be changed to 'airforce' for a production version of the script
#SUBREDDIT = 'airforce+airnationalguard'
SUBREDDIT = 'AFSCbot'


def main():

    # Initialize a logging object and have some examples below from the Python Doc page
    logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)
    logging.info(time.strftime(LOG_TIME_FORMAT) + "Starting script")

    # setup pid, database, and AFSC dict
    open_pid()
    conn, dbCommentRecord = setup_database()
    AFSCdict = get_AFSCs()

    # reddit user object
    reddit = login()

    # subreddit instance of /r/AirForce.
    rAirForce = reddit.subreddit(SUBREDDIT)

    process_comments(rAirForce, conn, dbCommentRecord, AFSCdict)


def open_pid():
    # Get the PID of this process
    # Exit if a version of the script is already running
    if os.path.isfile(PID_FILE):
        print("pid already open, exiting script")
        sys.exit(1)
    else:
        # Create the lock file for the script
        pid = str(os.getpid())
        open(PID_FILE, 'w').write(pid)


def login():
    try:
        creds = open(CRED_FILE, 'r')
        print("Opened creds file")
        logging.info(time.strftime(LOG_TIME_FORMAT) + "Opened creds file")
    except OSError:
        print("Couldn't open {}".format(CRED_FILE))
        logging.error(time.strftime(LOG_TIME_FORMAT) + "Couldn't open {}".format(CRED_FILE))
        sys.exit(1)

    agent = creds.readline().strip()
    ID = creds.readline().strip()
    secret = creds.readline().strip()
    client_user = creds.readline().strip()
    client_password = creds.readline().strip()
    creds.close()

    # Try to login or sleep/wait until logged in, or exit if user/pass wrong
    NotLoggedIn = True
    while NotLoggedIn:
        try:
            reddit = praw.Reddit(
                user_agent=agent,
                client_id=ID,
                client_secret=secret,
                username=client_user,
                password=client_password)
            print("Logged in")
            NotLoggedIn = False
        except praw.errors.InvalidUserPass:
            print("Wrong username or password")
            logging.error(time.strftime(LOG_TIME_FORMAT) + "Wrong username or password")
            exit(1)
        except Exception as err:
            print(str(err))
            time.sleep(5)
    return reddit


def setup_database():
    dbFile = Path(DB_FILE)

    # check to see if database file exists
    if dbFile.is_file():
        # connection to database file
        conn = sqlite3.connect(DB_FILE)
        # database cursor object
        dbCommentRecord = conn.cursor()

    else:  # if it doesn't, create it
        conn = sqlite3.connect(DB_FILE)
        dbCommentRecord = conn.cursor()
        dbCommentRecord.execute('''CREATE TABLE comments(comment text)''')
    return conn, dbCommentRecord


def get_AFSCs():
    # Load the AFSCs into a dictionary, then use the AFSC as the key to the Job Title
    AFSCdict = {}
    with open(AFSC_FILE, newline='') as f:
        reader = csv.reader(f, delimiter='#')
        for row in reader:
            afsc, jt = row
            AFSCdict[afsc] = jt

    if AFSCdict == {}:
        print("AFSC dict empty: exiting program")
        sys.exit(1)

    return AFSCdict


def process_comments(rAirForce, conn, dbCommentRecord, AFSCdict):
    logging.info(time.strftime(LOG_TIME_FORMAT) + "Starting processing loop for subreddit: " + SUBREDDIT)
    comments_seen = 0
    while True:
        try:
            # stream all comments from /r/AirForce
            for rAirForceComments in rAirForce.stream.comments():
                comments_seen += 1
                print("\nComments processed since start of script: " + str(comments_seen))
                print("Processing comment: " + rAirForceComments.id)

                # prints a link to the comment. A True for permalink generates a fast find (but is not an accurate link,
                # just makes the script faster (SIGNIFICANTLY FASTER)
                permlink = "http://www.reddit.com" + \
                           rAirForceComments.permalink(True) + "/"
                print(permlink)
                logging.info(time.strftime(LOG_TIME_FORMAT) +
                             "Processing comment: " + permlink)

                # Pulls all comments previously commented on
                dbCommentRecord.execute(
                    "SELECT * FROM comments WHERE comment=?", (rAirForceComments.id,))

                id_exists = dbCommentRecord.fetchone()

                # Make sure we don't reply to the same comment twice or to the bot
                # itself
                if id_exists:
                    print("Already processed comment: " +
                          str(rAirForceComments.id) + ", skipping")
                    continue
                elif rAirForceComments.author == "AFSCbot":
                    print("Author was the bot, skipping...")
                    continue
                else:
                    formattedComment = rAirForceComments.body.upper()

                    commentList = ""
                    matchList = []
                    for AFSC in AFSCdict.keys():
                        if AFSC in formattedComment:
                            matchList.append(AFSC)
                            commentList += AFSC + " = " + AFSCdict[AFSC] + "\n\n"
                        continue
                    if commentList != "":
                        print("Commenting on AFSC: " + str(matchList) + " by: " + str(rAirForceComments.author)
                              + ". Comment ID: " + rAirForceComments.id)
                        logging.info(time.strftime(LOG_TIME_FORMAT) +
                                     "Commenting on AFSC: " + str(matchList) + " by: " + str(rAirForceComments.author) + ". Comment ID: " +
                                     rAirForceComments.id)
                        CommentReply = '^^You\'ve ^^mentioned ^^an ^^AFSC, ^^here\'s ^^the ^^associated ^^job ^^title:\n\n' \
                                       + commentList

                        rAirForceComments.reply(CommentReply)
                        dbCommentRecord.execute(
                        'INSERT INTO comments VALUES (?);', (rAirForceComments.id,))
                        conn.commit()

        # what to do if Ctrl-C is pressed while script is running
        except KeyboardInterrupt:
            print("Keyboard Interrupt experienced, cleaning up and exiting")
            conn.commit()
            conn.close()
            print("Exiting due to keyboard interrupt")
            logging.info(time.strftime(LOG_TIME_FORMAT)
                         + "Exiting due to keyboard interrupt")
            os.unlink(PID_FILE)
            exit(0)

        except KeyError:
            print("AFSC not found in the dictionary, but the dict was called for some reason")
            logging.error(time.strftime(LOG_TIME_FORMAT)
                          + "AFSC not found in the dictionary, but the dict was called for some reason")

        except Exception as err:
            print("Exception: " + str(err))
            logging.error(time.strftime(LOG_TIME_FORMAT)
                          + "Unhandled exception: " + str(err))
    #os.unlink(PID_FILE)


if __name__ == "__main__":
    main()