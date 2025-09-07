#!/bin/bash

# Pull latest code from git
git pull

# Install updated requirements
pip install -r requirements.txt

# Stop the service
sudo systemctl stop algosy-ratings.service

# Start the service
sudo systemctl start algosy-ratings.service

echo "Algosy Ratings service updated and restarted"