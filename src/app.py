import uvicorn
import os
from fastapi import FastAPI, Query
from typing import Dict, List, Optional, Union, Any
import asyncio
from lib.fetchers.InformaticsFetcher import InformaticsFetcher
from lib.fetchers.InformaticsSessionReanimator import InformaticsSessionReanimator
from lib.fetchers.UsersFetcher import UsersFetcher
from lib.parsers.InformaticsParser import InformaticsParser
from lib.parsers.UsersParser import UsersParser
from lib.renderer.renderer import Renderer
from lib.global_data import GlobalData
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get interval settings from environment variables with defaults
REANIMATE_INTERVAL_MINUTES = int(os.getenv("REANIMATE_INTERVAL_MINUTES"))
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES"))
PARSE_INTERVAL_MINUTES = int(os.getenv("PARSE_INTERVAL_MINUTES"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Algosy Ratings API")


def reanimate():
    reanimators = [InformaticsSessionReanimator()]
    for reanimator in reanimators:
        reanimator.prepare()
        reanimator.process()

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
    reanimate()
    fetch_data()
    parse_data()
    
    # Set up scheduler to download CSV and update data based on environment settings
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reanimate, 'interval', minutes=REANIMATE_INTERVAL_MINUTES)
    scheduler.add_job(fetch_data, 'interval', minutes=FETCH_INTERVAL_MINUTES)
    scheduler.add_job(parse_data, 'interval', minutes=PARSE_INTERVAL_MINUTES)
    scheduler.start()
    logger.info(f"Scheduler started - will fetch data every {FETCH_INTERVAL_MINUTES} minutes and parse data every {PARSE_INTERVAL_MINUTES} minutes")

@app.get("/ratings")
async def get_participant_ratings(
    type: str = Query(None, description="Struct of response format"),
    mode: str = Query('short', description="Mode of response format")
):
    """
    Get ratings for all participants.
    
    Query Parameters:
    - type: If set to 'list', returns data in {handle: [name, rating]} format
    
    Returns:
        JSON with participant data sorted by rating (descending)
    """
    if type == "list":
        renderer = Renderer(mode)
        renderer.prepare()
        data = renderer.process()
            
        return data
    
    # Default response if type is not 'list'
    return {"error": "Invalid type parameter. Use '?type=list'"}

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)