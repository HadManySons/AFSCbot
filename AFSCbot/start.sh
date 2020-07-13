#!/bin/bash
#Starts an instance of AFSCbot with screen, with the session name AFSCbot and starts it detached
cd /src
#screen -S AFSCbot -d -m python3.8 /src/main.py
#screen -S AuthDelAFSCBot -d -m python3.8 /src/AuthDelete.py
set -m

python3.8 AuthDelete.py &
python3.8 main.py

fg%1
