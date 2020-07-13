# AFSCbot #

A bot for /r/airforce that scans comments for a mention of an AFSC and posts the matching job title

## Running as script ##
*BotCreds.py needs the correct credentials inputted before the script will run*

**python3.8 main.py**

## Running as docker container##
*You need to pass the BotCreds.py file into the container, as well as pass an environment variable for the SubReddit you want the bot to look at. Or, you can just edit the file manually and omit the "--mount" and "--env"*

*replace $ReplaceMe with the path to BotCreds.py

To run it locally:

**git clone https://github.com/hadmanysons/afscbot.git**

**cd AFSCbot**

**docker built -t afscbot .**

**docker run -d --env SUBREDDIT=AirForce --mount type=bind,source=$ReplaceMe/BotCreds.py,target=/src/BotCreds.py,readonly afscbot**

To run it from DockerHub:

**docker run -d --env SUBREDDIT=AirForce --mount type=bind,source=$ReplaceMe/BotCreds.py,target=/src/BotCreds.py,readonly hadmanysons/afscbot**