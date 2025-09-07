import os
import csv
import logging
from lib.codeforces_api import CodeforcesAPI
from typing import List, Dict, Optional, Tuple

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logger = logging.getLogger(__name__)

def read_participants_csv() -> Tuple[Dict[str, str], List[str]]:
    """
    Read participants data from CSV file.
    
    Returns:
        Tuple containing:
        - Dictionary mapping handles to names
        - List of handles
    """
    handles_to_names = {}
    handles = []
    
    try:
        csv_path = os.path.join(PROJECT_ROOT, "raw", "participants_list.csv")
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 3:
                    timestamp, name, handle = row
                    handles_to_names[handle] = name.strip()
                    handles.append(handle)
        
        logger.info(f"Read {len(handles)} participants from CSV")
        return handles_to_names, handles
    except Exception as e:
        logger.error(f"Error reading participants CSV: {str(e)}")
        return {}, []

def get_ratings(handles: List[str]) -> Dict[str, Optional[int]]:
    """
    Get ratings for a list of Codeforces handles.
    
    Args:
        handles: A list of Codeforces handles (usernames)
        
    Returns:
        A dictionary mapping each handle to its rating.
        If a user doesn't have a rating or doesn't exist, the value will be None.
    """
    requester = CodeforcesAPI()
    handles_param = ";".join(handles)
    data = requester.user_info({"handles": handles_param})
    # Create a dictionary to store the results
    ratings = {handle: 0 for handle in handles}
    for user in data["result"]:
        handle = user["handle"]
        # Some users might not have a rating
        rating = user.get("rating")
        ratings[handle] = rating
    
    return ratings