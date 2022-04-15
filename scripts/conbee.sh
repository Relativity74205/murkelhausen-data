#!/usr/bin/env bash

sudo gpasswd -a $USER dialout
wget -O - http://phoscon.de/apt/deconz.pub.key | sudo apt-key add -
sudo sh -c "echo 'deb http://phoscon.de/apt/deconz $(lsb_release -cs) main' > /etc/apt/sources.list.d/deconz.list"
sudo apt update && sudo apt install deconz

sudo systemctl enable deconz


