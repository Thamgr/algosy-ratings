import os
import requests
import logging
from dotenv import load_dotenv


class UsersFetcher():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def prepare(self):
        load_dotenv()
        self.USERS_SPREADSHEET_URL = os.environ.get('USERS_SPREADSHEET_URL')
        self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
        self.USERS_CSV_PATH = os.environ.get('USERS_CSV_PATH')
        return True


    def process(self):
        """
        Downloads data from a Google Spreadsheet and saves it as a CSV file.
        
        The function downloads data from the specified Google Spreadsheet and
        saves it to the path specified in USERS_CSV_PATH environment variable.
        
        Returns:
            bool: True if download was successful, False otherwise
        """
        
        try:
            # Download the CSV content
            response = requests.get(self.USERS_SPREADSHEET_URL)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Create the 'raw' directory if it doesn't exist
                csv_dir = os.path.dirname(os.path.join(self.PROJECT_ROOT, self.USERS_CSV_PATH))
                os.makedirs(csv_dir, exist_ok=True)
                
                # Save the content to the specified file
                output_path = os.path.join(self.PROJECT_ROOT, self.USERS_CSV_PATH)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                self.logger.info(f"CSV file successfully downloaded and saved to {output_path}")
                return True
            else:
                self.logger.error(f"Failed to download the CSV file. Status code: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading CSV file: {str(e)}")
            return False
