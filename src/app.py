import uvicorn
import os
from fastapi import FastAPI, Query
from typing import Dict, List, Optional, Union, Any
import asyncio
from lib.tools import get_ratings, read_participants_csv
from lib.download_spreadsheet import download_google_sheet_csv
from lib.fetchers.InformaticsFetcher import InformaticsFetcher
from lib.fetchers.UsersFetcher import UsersFetcher
from lib.parsers.InformaticsParser import InformaticsParser
from lib.parsers.UsersParser import UsersParser
from lib.renderer.renderer import Renderer
from lib.global_data import GlobalData
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


def fetch_data():
    fetchers = [InformaticsFetcher(), UsersFetcher()]
    for fetcher in fetchers:
        fetcher.prepare()
        fetcher.process()

def parse_data():
    fetchers = [InformaticsParser(), UsersParser()]
    for fetcher in fetchers:
        fetcher.prepare()
        fetcher.process()


@app.on_event("startup")
async def startup_event():
    """
    Initialize data and start the scheduler on application startup.
    """
    fetch_data()
    parse_data()
    
    # Set up scheduler to download CSV and update data every 6 hours
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_data, 'interval', hours=6)
    scheduler.add_job(parse_data, 'interval', hours=1)
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
        renderer = Renderer()
        renderer.Prepare()
        data = renderer.Process()
            
        return data
    
    # Default response if type is not 'list'
    return {"error": "Invalid type parameter. Use '?type=list'"}

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)