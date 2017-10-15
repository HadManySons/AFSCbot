import praw
import logging
import time
import os
import sys
from BotCreds import credsUserAgent, credsClientID, credsClientSecret, credsPassword, credsUserName

# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='DownvoteRemover.log', level=logging.INFO)

# Get the PID of this process
pid = str(os.getpid())
pidfile = "DownvoteDelete.pid"

# Exit if a version of the script is already running
if os.path.isfile(pidfile):
    print(pidfile + " already running, exiting")
    sys.exit()

# Create the lock file for the script
open(pidfile, 'w').write(pid)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") + "Starting script")

# Try to login or sleep/wait until logged in, or exit if user/pass wrong
NotLoggedIn = True
while NotLoggedIn:
    try:
        reddit = praw.Reddit(
            user_agent=credsUserAgent.strip(),
            client_id=credsClientID.strip(),
            client_secret=credsClientSecret.strip(),
            username=credsUserName.strip(),
            password=credsPassword.strip())
        print("Logged in")
        NotLoggedIn = False
    except praw.errors.InvalidUserPass:
        print("Wrong username or password")
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") + "Wrong username or password")
        exit(1)
    except Exception as err:
        print(err)
        time.sleep(5)

# vars
globalCount = 0
deleteThreshold = 1


logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
             "Starting processing loop for comments")

#reads all comments the bot ever made...ALL
def proccessComments():
    for comment in reddit.redditor(str(reddit.user.me())).comments.new(limit=None):
        #if comment score is below the threshold, delete it
        if comment.score < deleteThreshold:
            comment.delete()

            permalink = "http://www.reddit.com" + \
                                   comment.permalink() + "/"

            print("Deleting comment: " + permalink)
            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                         "Deleting comment: " + permalink)


try:
    while True:
        #check the comments
        proccessComments()
        #wait x amount of seconds before trying again
        time.sleep(300)

# what to do if Ctrl-C is pressed while script is running
except KeyboardInterrupt:
    print("Keyboard Interrupt experienced, cleaning up and exiting")
    print("Exiting due to keyboard interrupt")
    logging.info(time.strftime("%Y/%m/%d %H:%M:%S ")
                 + "Exiting due to keyboard interrupt")
    exit(0)

except Exception as err:
    print("Exception: " + str(err.with_traceback()))
    logging.error(time.strftime("%Y/%m/%d %H:%M:%S ")
                  + "Unhandled exception: " + + str(err.with_traceback()))

finally:
    os.unlink(pidfile)