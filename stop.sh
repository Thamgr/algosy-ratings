#!/bin/bash

# Stop the service
sudo systemctl stop algosy-ratings.service

# Disable the service
sudo systemctl disable algosy-ratings.service

echo "Algosy Ratings service stopped"