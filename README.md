# AFSCbot #

[![Docker Image CI](https://github.com/HadManySons/AFSCbot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/HadManySons/AFSCbot/actions/workflows/docker-image.yml)

A bot for /r/airforce that scans comments for a mention of an AFSC and posts the matching job title

*AFS_ENVS.list needs the correct credentials inputted before the script will run*

## Running as docker container ##
*You need to pass the environment variables with the `--env-file` flag*

To run it locally:

`git clone https://github.com/hadmanysons/afscbot.git`

`cd AFSCbot`

`docker built -t afscbot .`

`docker run -d -v afscbot:/app --env-file ./AFS_ENVS.list --restart unless-stopped --name afscbot afscbot:latest`
