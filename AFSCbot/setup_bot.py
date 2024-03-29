from pathlib import Path
import praw
import os
import sys
import time

from helper_functions import print_and_log

def login(username, password, client_secret, client_id, user_agent):

    # Try to login or sleep/wait until logged in, or exit if user/pass wrong
    NotLoggedIn = True
    while NotLoggedIn:
        try:
            reddit = praw.Reddit(
                user_agent=user_agent,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password)
            print_and_log("Logged in")
            NotLoggedIn = False
        except praw.errors.InvalidUserPass:
            print_and_log("Wrong username or password", error=True)
            exit(1)
        except Exception as err:
            print_and_log(str(err), error=True)
            time.sleep(5)
    return reddit
