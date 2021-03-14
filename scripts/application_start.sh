#!/bin/bash

#Create Env
cd /home/ec2-user
mkdir -p .venv
python3 -m venv ./.venv/SteamCommunityBotEnv

#Activate Env
source .venv/SteamCommunityBotEnv/bin/activate
sudo python3 -m pip install -U pip

#Install dependencies
python3 -m pip install -r /home/ec2-user/SteamCommunityBot/requirements.txt

#Copy latest service file to correct folder
sudo cp /home/ec2-user/SteamCommunityBot/steam-community-bot.service /lib/systemd/system/steam-community-bot.service
sudo systemctl daemon-reload
sudo systemctl enable steam-community-bot.service
sudo systemctl start steam-community-bot.service