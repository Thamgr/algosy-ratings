#!/bin/bash

# Install Python requirements
pip3 install -r requirements.txt

# Copy service file to systemd directory
sudo cp algosy-ratings.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable algosy-ratings.service
sudo systemctl start algosy-ratings.service

echo "Algosy Ratings service started"