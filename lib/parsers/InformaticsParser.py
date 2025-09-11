import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from lib.global_data import GlobalData
from typing import Dict, Tuple

class InformaticsParser():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.PROJECT_ROOT = None
        self.INFORMATICS_DIR = None
        self.CONTEST_IDS = []
        self.BANNED_NAMES = []

    def prepare(self):
        """
        Load environment variables and set up paths.
        
        Returns:
            bool: True if preparation was successful, False otherwise
        """
        try:
            load_dotenv()
            self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.INFORMATICS_DIR = os.environ.get('INFORMATICS_DIR', os.path.join('raw', 'informatics'))
            
            # Get contest IDs from environment variable
            contest_ids_str = os.environ.get('INFORMATICS_CONTEST_IDS', '')
            self.CONTEST_IDS = [id.strip() for id in contest_ids_str.split(',') if id.strip()]

            banned_names_str = os.environ.get('BANNES_NAMES_STR', '')
            self.BANNED_NAMES = [name.strip() for name in banned_names_str.split(',') if name.strip()]
            self.logger.info(f"Got banned_names for informatics: {str(self.BANNED_NAMES)}")
            
            self.logger.info(f"Using Informatics directory: {self.INFORMATICS_DIR}")
            self.logger.info(f"Contest IDs to process: {self.CONTEST_IDS}")
            return True
        except Exception as e:
            self.logger.error(f"Error preparing InformaticsParser: {str(e)}")
            return False

    def process_single(self, id) -> Tuple[Dict[str, int], int]:
        """
        Parse a single contest file and return a dictionary with participant names and their number of solved problems,
        along with the total number of problems in the contest.
        
        Args:
            id (str): Contest ID
            
        Returns:
            tuple: (
                dict: Dictionary with participant names as keys and number of pluses as values,
                int: Number of problems in the contest
            )
        """
        # Construct the file path
        file_path = os.path.join(self.PROJECT_ROOT, self.INFORMATICS_DIR, f'contest_{id}')
        
        # Dictionary to store results
        results = {}
        problem_count = 0
        
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                self.logger.error(f"Contest file not found at {file_path}")
                return {}, 0
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the main table with results
            table = soup.find('table', {'class': 'BlueTable'})
            if not table:
                self.logger.error(f"No results table found in contest {id}")
                return {}, 0
            
            # Find the header row to count problems
            header_row = table.find('tr')
            if header_row:
                # Count the number of problem columns (excluding N, Name, and Sum columns)
                problem_columns = header_row.find_all('td')[3:]
                problem_count = len(problem_columns)
            
            # Find all participant rows (skip header rows)
            rows = table.find_all('tr')
            for row in rows:
                # Skip header rows (they have 'N' in the first cell)
                first_cell = row.find('td')
                if not first_cell or first_cell.text.strip() == 'N':
                    continue
                
                # Extract participant name
                name_cell = row.find_all('td')[1]
                name_link = name_cell.find('a')
                if not name_link:
                    continue
                
                name = name_link.text.strip()

                if name in self.BANNED_NAMES:
                    continue
                
                # Count pluses (solved problems)
                pluses = 0
                problem_cells = row.find_all('td')[3:]  # Skip position, name, and sum cells
                
                for cell in problem_cells:
                    cell_text = cell.text.strip()
                    # Count as solved if the cell contains a plus sign
                    if '+' in cell_text:
                        pluses += 1
                
                # Add to results
                results[name] = pluses
            
            self.logger.info(f"Parsed contest {id} with {len(results)} participants and {problem_count} problems")
            return results, problem_count
        except Exception as e:
            self.logger.error(f"Error parsing contest {id}: {str(e)}")
            return {}, 0

    def process(self):
        """
        Process all contests specified in INFORMATICS_CONTEST_IDS environment variable.
        Also updates the GlobalData instance with the parsed data.
        
        Returns:
            dict: Dictionary with participant names as keys and lists of solved problems as values.
                  Each list contains the number of problems solved by the participant in each contest,
                  in the order specified in INFORMATICS_CONTEST_IDS. If a participant didn't
                  participate in a contest, their result for that contest is 0.
        """
        if not self.CONTEST_IDS:
            self.logger.error("No contest IDs found in environment variable INFORMATICS_CONTEST_IDS")
            return {}
            
        # Dictionary to store all participants across all contests
        all_participants = set()
        
        # Dictionary to store results for each contest
        contest_results = {}
        
        # List to store the number of problems in each contest
        contest_problem_counts = []
        
        # Process each contest
        for contest_id in self.CONTEST_IDS:
            # Get the results and problem count for the contest
            results, problem_count = self.process_single(contest_id)
            contest_results[contest_id] = results
            contest_problem_counts.append(problem_count)
            all_participants.update(results.keys())
        
        # Create the final results dictionary
        final_results = {}
        
        # For each participant, create a list of their results for each contest
        for participant in all_participants:
            participant_results = []
            
            for contest_id in self.CONTEST_IDS:
                # Get the participant's result for this contest, or 0 if they didn't participate
                result = contest_results[contest_id].get(participant, 0)
                participant_results.append(result)
            
            final_results[participant] = participant_results
        
        self.logger.info(f"Processed {len(self.CONTEST_IDS)} contests with {len(final_results)} total participants")
        
        # Update the global data
        GlobalData().update_informatics_data(final_results)
        GlobalData().update_informatics_common_data(contest_problem_counts)
        
        return final_results
