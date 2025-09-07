#!/bin/bash

# Check the status of the service
sudo systemctl status algosy-ratings.service

# Show the last few log entries
echo -e "\nRecent logs:"
sudo journalctl -u algosy-ratings.service -n 20 --no-pager