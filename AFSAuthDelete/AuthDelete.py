import praw
import logging
import time
import os
from helper_functions import print_and_log

#get creds from environment variables
credsUserAgent = os.environ.get("AFS_USERAGENT")
credsClientID = os.environ.get("AFS_ID")
credsClientSecret = os.environ.get("AFS_SECRET")
credsPassword = os.environ.get("AFS_PASSWORD")
credsUserName = os.environ.get("AFS_USERNAME")

# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='AuthDelete.log', level=logging.INFO)

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
        print_and_log("Logged in")
        NotLoggedIn = False
    except praw.errors.InvalidUserPass:
        print_and_log("Wrong username or password")
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") + "Wrong username or password")
        exit(1)
    except Exception as err:
        print_and_log(err)
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
            print_and_log("\nComments processed since start of script: " + str(globalCount))
            print_and_log("Processing comment: " + rAirForceComments.id)
            print_and_log("Submission: {}".format(str(rAirForceComments.submission)))
            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                         "Processing comment: " + rAirForceComments.id)

            #If, for some odd reason, the bot is the author, ignore it.
            if rAirForceComments.author == "AFSCbot":
                print_and_log("Author was the bot, skipping...")
                continue
            else:
                #Get the parent comment(the bot) and grandparent(comment originally replied to)
                parent = rAirForceComments.parent()
                grandparent = parent.parent()

                formattedComment = rAirForceComments.body
                formattedComment = formattedComment.lower()
                formattedComment = formattedComment.replace(' ', '')

                #Shutdown bot if mod commands it
                if "shutdown!" in formattedComment and rAirForceComments.author == ("HadManySons" or "SilentD"):
                    os.system("cat /home/redditbots/bots/AFILinkerBot/AFILinkerBot.pid | xargs kill -9")
            
                if "deletethis!" in formattedComment:
                        #Must be the original comment author
                        if rAirForceComments.author == grandparent.author:
                            print_and_log("Deleting comment per redditors request")
                            rAirForceComments.parent().delete()
                            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                                     "Deleting comment: " + rAirForceComments.id)

                            #Let them know we deleted the comment
                            rAirForceComments.author.message("Comment deleted", "Comment deleted: " + rAirForceComments.id)

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print_and_log("Keyboard Interrupt experienced, cleaning up and exiting")
        print_and_log("Exiting due to keyboard interrupt")
        logging.info(time.strftime("%Y/%m/%d %H:%M:%S ")
                     + "Exiting due to keyboard interrupt")
        exit(0)

    except Exception as err:
        print_and_log("Exception: " + str(err.with_traceback()))
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ")
                      + "Unhandled exception: " + + str(err.with_traceback()))
