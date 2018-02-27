import praw
import logging
import time
import os
import sys
from BotCreds import credsUserAgent, credsClientID, credsClientSecret, credsPassword, credsUserName

# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='AuthDelete.log', level=logging.INFO)

# Get the PID of this process
pid = str(os.getpid())
pidfile = "AuthDelete.pid"

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

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
             "Starting processing loop for comments")

while True:
    try:
        # stream all unread messages from inbox
        for rAirForceComments in reddit.inbox.stream():
            globalCount += 1

            #Marks the comment as read
            rAirForceComments.mark_read()

            #print(unread_messages)
            print("\nComments processed since start of script: " + str(globalCount))
            print("Processing comment: " + rAirForceComments.id)
            print("Submission: {}".format(str(rAirForceComments.submission)))
            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                         "Processing comment: " + rAirForceComments.id)

            #If, for some odd reason, the bot is the author, ignore it.
            if rAirForceComments.author == "AFILinkerBot":
                print("Author was the bot, skipping...")
                continue
            else:
                #Get the parent comment(the bot) and grandparent(comment originally replied to)
                parent = rAirForceComments.parent()
                grandparent = parent.parent()

                formattedComment = rAirForceComments.body
                formattedComment = formattedComment.lower()
                formattedComment = formattedComment.replace(' ', '')


                if "deletethis!" in formattedComment:
                        #Must be the original comment author
                        if rAirForceComments.author == grandparent.author:
                            print("Deleting comment per redditors request")
                            rAirForceComments.parent().delete()
                            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                                     "Deleting comment: " + rAirForceComments.id)

                            #Let them know we deleted the comment
                            rAirForceComments.author.message("Comment deleted", "Comment deleted: " + rAirForceComments.id)

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