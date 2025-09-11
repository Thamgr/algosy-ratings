import os
import csv
import logging
from dotenv import load_dotenv
from lib.global_data import GlobalData
from lib.codeforces_api import CodeforcesAPI
from typing import Dict, List, Optional

class UsersParser():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.csv_path = None
        self.PROJECT_ROOT = None

    def prepare(self):
        """
        Load environment variables and set up paths.
        
        Returns:
            bool: True if preparation was successful, False otherwise
        """
        try:
            load_dotenv()
            self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
            # Get CSV path from environment variable or use default
            csv_relative_path = os.environ.get('USERS_CSV_PATH', 'raw/participants_list.csv')
            self.csv_path = os.path.join(self.PROJECT_ROOT, csv_relative_path)
            
            self.logger.info(f"Using CSV path: {self.csv_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error preparing UsersParser: {str(e)}")
            return False

    def get_ratings(self, handles: List[str]) -> Dict[str, Optional[int]]:
        """
        Get ratings for a list of Codeforces handles.
        
        Args:
            handles: A list of Codeforces handles (usernames)
            
        Returns:
            A dictionary mapping each handle to its rating.
            If a user doesn't have a rating or doesn't exist, the value will be 0.
        """
        requester = CodeforcesAPI()
        handles_param = ";".join(handles)
        data = requester.user_info({"handles": handles_param})
        
        # Create a dictionary to store the results
        ratings = {handle: 0 for handle in handles}
        
        if "result" in data:
            for user in data["result"]:
                handle = user["handle"]
                # Some users might not have a rating
                rating = user.get("rating", 0)
                ratings[handle] = rating
        
        self.logger.info(f"Retrieved ratings for {len(handles)} handles")
        return ratings

    def process(self):
        """
        Read participants data from CSV file, get their Codeforces ratings,
        and return a dictionary mapping handles to dictionaries with name and rating.
        Also updates the GlobalData instance with the parsed data.
        
        Returns:
            dict: Dictionary mapping handles to dictionaries with name and rating
        """
        handles_to_data = {}
        
        try:
            if not os.path.exists(self.csv_path):
                self.logger.error(f"CSV file not found at {self.csv_path}")
                return {}
                
            # Read participants data from CSV
            handles_to_names = {}
            handles = []
            
            with open(self.csv_path, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                for row in reader:
                    if len(row) >= 3:
                        timestamp, name, handle = row
                        handles_to_names[handle] = name.strip()
                        handles.append(handle)
            
            self.logger.info(f"Read {len(handles_to_names)} participants from CSV")
            
            # Get ratings for all handles
            ratings = self.get_ratings(handles)
            
            # Combine the data
            for handle in handles:
                handles_to_data[handle] = {
                    "name": handles_to_names.get(handle, ""),
                    "rating": ratings.get(handle, 0)
                }
            
            # Update the global data
            GlobalData().update_users_data(handles_to_data)
            
            return handles_to_data
        except Exception as e:
            self.logger.error(f"Error processing users data: {str(e)}")
            return {}

def parse_users():
    """
    Convenience function to parse users using the UsersParser class.
    
    Returns:
        dict: Dictionary mapping handles to dictionaries with name and rating
    """
    parser = UsersParser()
    parser.prepare()
    return parser.process()
