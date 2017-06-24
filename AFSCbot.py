import praw
import sqlite3
from pathlib import Path
import random
import logging
import time
import os
import sys
import csv
# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='AFSCbot.log', level=logging.INFO)

# Get the PID of this process
pid = str(os.getpid())
pidfile = "AFSCbot.pid"

# Exit if a version of the script is already running
if os.path.isfile(pidfile):
    print(pidfile + " already running, exiting")
    sys.exit()

# Create the lock file for the script
open(pidfile, 'w').write(pid)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") + "Starting script")

# reddit user object
try:
    creds = open('AFSCbotCreds.txt', 'r')
    print("Opened creds file")
    logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") + "Opened creds file")
except OSError:
    print("Couldn't open ExcusesCreds.txt")
    logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") + "Couldn't open AFSCbotCreds.txt")
    exit()

credsUserAgent = creds.readline()
credsClientID = creds.readline()
credsClientSecret = creds.readline()
credsUsername = creds.readline()
credsPassword = creds.readline()
creds.close()

# Try to login or sleep/wait until logged in, or exit if user/pass wrong
NotLoggedIn = True
while NotLoggedIn:
    try:
        reddit = praw.Reddit(
            user_agent=credsUserAgent.strip(),
            client_id=credsClientID.strip(),
            client_secret=credsClientSecret.strip(),
            username=credsUsername.strip(),
            password=credsPassword.strip())
        print("Logged in")
        NotLoggedIn = False
    except praw.errors.InvalidUserPass:
        print("Wrong username or password")
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") + "Wrong username or password")
        exit(1)
    except Exception as err:
        print(str(err))
        time.sleep(5)

# vars
globalCount = 0
dbFile = Path("AFSCbotCommentRecord.db")

# check to see if database file exists
if dbFile.is_file():
    # connection to database file
    conn = sqlite3.connect("AFSCbotCommentRecord.db")
    # database cursor object
    dbCommentRecord = conn.cursor()
else:  # if it doesn't, create it
    conn = sqlite3.connect("AFSCbotCommentRecord.db")
    dbCommentRecord = conn.cursor()
    dbCommentRecord.execute('''CREATE TABLE comments(comment text)''')

# subreddit instance of /r/AirForce. 'AFSCbot' must be changed to 'airforce' for a production version of the
# script.
#subreddit = 'airforce+airnationalguard'
subreddit = 'AFSCbot'
rAirForce = reddit.subreddit(subreddit)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
             "Starting processing loop for subreddit: " + subreddit)

AFSCdict = {}
AFSClist =  []

with open('AFSClist.csv', newline='') as f:
    reader = csv.reader(f, delimiter='#')
    for row in reader:
        afsc, jt = row
        AFSCdict[afsc] = jt

for keys in AFSCdict.keys():
    AFSClist.append(keys)

while True:
    try:
        # stream all comments from /r/AirForce
        for rAirForceComments in rAirForce.stream.comments():
            globalCount += 1
            print("\nComments processed since start of script: " + str(globalCount))
            print("Processing comment: " + rAirForceComments.id)

            # prints a link to the comment. A True for permalink generates a fast find (but is not an accurate link,
            # just makes the script faster (SIGNIFICANTLY FASTER)
            permlink = "http://www.reddit.com" + \
                       rAirForceComments.permalink(True) + "/"
            print(permlink)
            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
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
                formattedComment = rAirForceComments.body
                formattedComment = formattedComment.upper()

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
                    logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
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
        logging.info(time.strftime("%Y/%m/%d %H:%M:%S ")
                     + "Exiting due to keyboard interrupt")
        exit(0)

    except KeyError:
        print("AFSC not found in the dictionary, but the dict was called for some reason")
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ")
                      + "AFSC not found in the dictionary, but the dict was called for some reason")


    except Exception as err:
        print("Exception: " + str(err))
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ")
                      + "Unhandled exception: " + str(err))


    finally:
        os.unlink(pidfile)