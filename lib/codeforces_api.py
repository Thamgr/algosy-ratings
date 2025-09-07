import requests
from typing import List, Dict, Any, Optional


class CodeforcesAPI:
    """
    A class for interacting with the Codeforces API.
    
    This class provides methods to retrieve data from the Codeforces API,
    such as user ratings.
    """
    
    BASE_URL = "https://codeforces.com/api"
    
    def __init__(self):
        """Initialize the CodeforcesAPI class."""
        pass

    def user_info(self, params={}):
        url = f"{self.BASE_URL}/user.info"
        data = {}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
        except Exception as e:
            print(f"Error while fetching ratings: {str(e)}")
        return data


