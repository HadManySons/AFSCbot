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
    print_and_log("Starting script")

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
        print_and_log("PID already open, exiting script", error=True)
        sys.exit(1)
    else:
        # Create the lock file for the script
        pid = str(os.getpid())
        open(PID_FILE, 'w').write(pid)


def login():
    try:
        creds = open(CRED_FILE, 'r')
        print_and_log("Opened creds file")
    except OSError:
        print_and_log("Couldn't open {}".format(CRED_FILE), error=True)
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
            print_and_log("Logged in")
            NotLoggedIn = False
        except praw.errors.InvalidUserPass:
            print_and_log("Wrong username or password", error=True)
            exit(1)
        except Exception as err:
            print_and_log(str(err), error=True)
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
    print_and_log("Starting processing loop for subreddit: " + SUBREDDIT)
    comments_seen = 0
    try:
        while True:
            try:
                # stream all comments from /r/AirForce
                for rAirForceComment in rAirForce.stream.comments():
                    comments_seen += 1
                    print()
                    print("Comments processed since start of script: " + str(comments_seen))
    
                    # prints a link to the comment. A True for permalink generates a fast find (but is not an accurate link,
                    # just makes the script faster (SIGNIFICANTLY FASTER)
                    permlink = "http://www.reddit.com" + rAirForceComment.permalink(True) + "/"

                    print_and_log("Processing comment: " + permlink)
    
                    # Pulls all comments previously commented on
                    dbCommentRecord.execute("SELECT * FROM comments WHERE comment=?", (rAirForceComment.id,))
    
                    id_exists = dbCommentRecord.fetchone()
    
                    # Make sure we don't reply to the same comment twice or to the bot itself
                    if id_exists:
                        print("Already processed comment: {}, skipping".format(rAirForceComment.id))
                    elif rAirForceComment.author == "AFSCbot":
                        print("Author was the bot, skipping...")
                    else:
                        formattedComment = rAirForceComment.body.upper()
    
                        commentText = ""
                        matchList = []
                        for AFSC in AFSCdict.keys():
                            if AFSC in formattedComment:
                                matchList.append(AFSC)
                                commentText += "{} = {}\n\n".format(AFSC, AFSCdict[AFSC])

                        if commentText != "":
                            comment_info_text = "Commenting on AFSC: {} by: {}. Comment ID: {}".format(
                                                matchList, rAirForceComment.author, rAirForceComment.id)
                            print_and_log(comment_info_text)

                            commentHeader = "^^You've ^^mentioned ^^an ^^AFSC, ^^here's ^^the ^^associated ^^job ^^title:\n\n"
                            rAirForceComment.reply(commentHeader + commentText)

                            dbCommentRecord.execute('INSERT INTO comments VALUES (?);', (rAirForceComment.id,))
                            conn.commit()
    
            # what to do if Ctrl-C is pressed while script is running
            except KeyboardInterrupt:
                print_and_log("Exiting due to keyboard interrupt", error=True)
                sys.exit(0)
    
            except KeyError:
                print_and_log("AFSC not found in the dictionary, but the dict was called for some reason", error=True)
    
            except Exception as err:
                print_and_log("Unhandled Exception: " + str(err), error=True)
    
            finally:
                conn.commit()
    finally:
        conn.commit()
        conn.close()
        os.unlink(PID_FILE)


def print_and_log(text, error=False):
    print(text)
    if error:
        logging.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logging.info(time.strftime(LOG_TIME_FORMAT) + text)


if __name__ == "__main__":
    main()
