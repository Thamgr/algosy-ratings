import os
import requests
import logging

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logger = logging.getLogger(__name__)

def download_google_sheet_csv():
    """
    Downloads data from a Google Spreadsheet and saves it as a CSV file.
    
    The function downloads data from the specified Google Spreadsheet and
    saves it to raw/participants_list.csv.
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    # Extract spreadsheet ID and GID from the URL
    spreadsheet_id = "1gkGokOmmY8Y-5VP5hF-iRRcDzCzC0e9fjhm2pg5i_E0"
    gid = "1230935448"
    
    # Construct the export URL
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    
    try:
        # Download the CSV content
        response = requests.get(export_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Create the 'raw' directory if it doesn't exist
            raw_dir = os.path.join(PROJECT_ROOT, "raw")
            os.makedirs(raw_dir, exist_ok=True)
            
            # Save the content to the specified file
            output_path = os.path.join(PROJECT_ROOT, "raw", "participants_list.csv")
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"CSV file successfully downloaded and saved to {output_path}")
            return True
        else:
            logger.error(f"Failed to download the CSV file. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error downloading CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    download_google_sheet_csv()
