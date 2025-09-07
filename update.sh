#!/bin/bash

# Pull latest code from git
git pull

# Stop the service
sudo systemctl stop algosy-ratings.service

# Call start.sh to handle environment setup and service start
sudo ./start.sh

echo "Algosy Ratings service updated and restarted"