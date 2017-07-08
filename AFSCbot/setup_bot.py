from pathlib import Path
import praw
import sqlite3
import os
import sys

from helper_functions import print_and_log

CRED_FILE = 'AFSCbotCreds.txt'
DB_FILE = "AFSCbotCommentRecord.db"
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

    # connection to database file
    conn = sqlite3.connect(DB_FILE)
    # database cursor object
    dbCommentRecord = conn.cursor()

    # check to see if database file exists
    if not dbFile.is_file():
        dbCommentRecord.execute('''CREATE TABLE comments(comment text)''')
        conn.commit()
    return conn, dbCommentRecord