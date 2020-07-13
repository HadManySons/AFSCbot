from pathlib import Path
import praw
import sqlite3
import os
import sys
import time
from BotCreds import credsUserAgent,credsClientID, credsClientSecret, credsUserName, credsPassword

from helper_functions import print_and_log

DB_FILE = "./AFSCbotCommentRecord.db"
PID_FILE = "AFSCbot.pid"


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


def close_pid():
    os.unlink(PID_FILE)


def login():

    # Try to login or sleep/wait until logged in, or exit if user/pass wrong
    NotLoggedIn = True
    while NotLoggedIn:
        try:
            reddit = praw.Reddit(
                user_agent=credsUserAgent,
                client_id=credsClientID,
                client_secret=credsClientSecret,
                username=credsUserName,
                password=credsPassword)
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
    # connection to database file
    conn = sqlite3.connect(DB_FILE)
    # database cursor object
    dbCommentRecord = conn.cursor()
    # check to see if table exists
    dbCommentRecord.execute('''CREATE TABLE IF NOT EXISTS comments(comment text)''')
    return conn, dbCommentRecord
