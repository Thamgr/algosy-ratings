#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    sudo python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python requirements
pip3 install -r requirements.txt

# Deactivate virtual environment
deactivate

# Update service file to use the virtual environment and current directory
sed -i "s|ExecStart=.*|ExecStart=$(pwd)/venv/bin/python -m uvicorn src.app:app --host 0.0.0.0 --port 8000|" algosy-ratings.service
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$(pwd)|" algosy-ratings.service

# Copy service file to systemd directory
sudo cp algosy-ratings.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable algosy-ratings.service
sudo systemctl start algosy-ratings.service

echo "Algosy Ratings service started"