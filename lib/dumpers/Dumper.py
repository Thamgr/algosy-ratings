import csv
import os
import logging
from datetime import datetime
from lib.renderer.renderer import Renderer

class Dumper:
    """
    Class for dumping data from Renderer to CSV files.
    """
    
    def __init__(self):
        """
        Initialize the Dumper with a Renderer instance.
        """
        self.logger = logging.getLogger(__name__)
        self.renderer = Renderer(mode='dumper')  # Use 'dumper' mode to get process_dump data
        self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
        self.SNAPSHOTS_PATH = os.environ.get('SNAPSHOTS_PATH')

    def prepare(self):
        # Create snapshots directory if it doesn't exist
        if not os.path.exists(self.SNAPSHOTS_PATH):
            os.makedirs(self.SNAPSHOTS_PATH)
            self.logger.info(f"Created snapshots directory: {self.SNAPSHOTS_PATH}")
    
    def process(self):
        """
        Fetch data from Renderer.process_dump and save it to a CSV file.
        The filename includes the current date and time.
        
        Returns:
            str: Path to the created CSV file or None if an error occurred
        """
        try:
            # Prepare the renderer data
            if not self.renderer.prepare():
                self.logger.error("Failed to prepare renderer data")
                return
            
            # Process the data using process() which will call process_dump() in 'dumper' mode
            data = self.renderer.process()
            if not data:
                self.logger.error("No data to dump")
                return
            
            # Generate filename with current date and time
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(self.PROJECT_ROOT, f"{self.SNAPSHOTS_PATH}/ratings_{timestamp}.csv")
            
            # Set fieldnames for the CSV based on the process_dump format
            fieldnames = ['handle', 'name', 'rating', 'solved']
            
            # Write to CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data.values())  # data.values() contains the dictionaries with participant data
            
            self.logger.info(f"Successfully dumped data to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error dumping data: {str(e)}")
            return