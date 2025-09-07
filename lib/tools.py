from lib.codeforces_api import CodeforcesAPI
from typing import List, Dict, Optional


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