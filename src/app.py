import uvicorn
import os
from fastapi import FastAPI, Query
from typing import Dict, List, Optional, Union, Any
import asyncio
from lib.tools import get_ratings, read_participants_csv
from lib.download_spreadsheet import download_google_sheet_csv
from lib.fetchers.InformaticsFetcher import InformaticsFetcher
from lib.fetchers.UsersFetcher import UsersFetcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Codeforces Ratings API")

# Global variable to store participants data
participants_data = {}

def update_participants_data():
    """
    Load participants data from CSV and fetch their ratings.
    This function can be called on startup and by the scheduler.
    """
    global participants_data
    
    try:
        # Read participants from CSV
        handles_to_names, handles = read_participants_csv()
        
        if not handles:
            logger.warning("No handles found in CSV file")
            return
        
        # Get ratings for all handles
        ratings = get_ratings(handles)

        for handle, rating in ratings.items():
            name = handles_to_names.get(handle, "Unknown")
            # Replace None ratings with 0
            rating_value = 0 if rating is None else rating
            participants_data[handle] = [name, rating_value]

        logger.info(f"Updated data for {len(participants_data)} participants at {datetime.now()}")
    except Exception as e:
        logger.error(f"Error updating participants data: {str(e)}")


def fetch_data():
    fetchers = [InformaticsFetcher(), UsersFetcher()]
    for fetcher in fetchers:
        fetcher.prepare()
        fetcher.process()


@app.on_event("startup")
async def startup_event():
    """
    Initialize data and start the scheduler on application startup.
    """

    fetch_data()
    
    # Set up scheduler to download CSV and update data every 6 hours
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_data, 'interval', hours=6)
    scheduler.add_job(update_participants_data, 'interval', hours=1)
    scheduler.start()
    logger.info("Scheduler started - will download CSV and update ratings every 6 hours")

@app.get("/ratings")
async def get_participant_ratings(
    type: str = Query(None, description="Type of response format")
):
    """
    Get ratings for all participants.
    
    Query Parameters:
    - type: If set to 'list', returns data in {handle: [name, rating]} format
    
    Returns:
        JSON with participant data sorted by rating (descending)
    """
    if type == "list":
        # Sort participants by rating (descending)
        sorted_data = {}
        # First, create a list of (handle, [name, rating]) tuples
        items = [(handle, data) for handle, data in participants_data.items()]
        # Sort by rating (index 1 in the data list), handling None values
        # Since we're replacing None with 0, we can simply sort by negative rating
        sorted_items = sorted(
            items,
            key=lambda x: -x[1][1]  # Sort by negative rating for descending order
        )
        # Convert back to dictionary
        for handle, data in sorted_items:
            sorted_data[handle] = data
            
        return sorted_data
    
    # Default response if type is not 'list'
    return {"error": "Invalid type parameter. Use '?type=list'"}

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)