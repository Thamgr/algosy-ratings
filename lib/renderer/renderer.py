import logging
from lib.global_data import GlobalData
from typing import Dict, List, Any, Union

class Renderer:
    """
    Class for rendering data from GlobalData into the required format.
    """
    
    def __init__(self, mode='short'):
        self.logger = logging.getLogger(__name__)
        self.participants_data = {}
        self.MAX_RATING = 2000  # Maximum rating to normalize by
        self.MAX_SOLVED = 0     # Will be calculated from global_data
        self.mode = mode
    
    def prepare(self):
        """
        Merge available fields from GlobalData by name and render an object for each participant.
        
        The rendered object has the structure:
        {
            handle: handle,
            name: name,
            rating: rating,
            solved: solved
        }
        
        This method stores the rendered data in the participants_data class variable.
        
        Returns:
            bool: True if preparation was successful, False otherwise
        """
        try:
            # Get data from GlobalData
            users_data = GlobalData().get_users_data()
            informatics_data = GlobalData().get_informatics_data()
            informatics_common_data = GlobalData().get_informatics_common_data()
            
            # Calculate MAX_SOLVED from informatics_common_data
            self.MAX_SOLVED = sum(informatics_common_data) if informatics_common_data else 1
            self.logger.info(f"Total number of problems (MAX_SOLVED): {self.MAX_SOLVED}")
            
            if not users_data:
                self.logger.warning("No users data available in GlobalData")
                return False
                
            # Create a mapping from names to handles
            names_to_handles = {}
            for handle, data in users_data.items():
                name = data.get("name", "")
                if name:
                    names_to_handles[name] = handle
            
            # Merge data and create participants_data
            self.participants_data = {}
            
            # First, add all users from users_data
            for handle, data in users_data.items():
                name = data.get("name", "")
                rating = data.get("rating", 0)
                
                # Find solved problems from informatics_data if available
                solved = 0
                if name in informatics_data:
                    # Sum all solved problems across all contests
                    solved = sum(informatics_data[name])
                
                self.participants_data[handle] = {
                    "handle": handle,
                    "name": name,
                    "rating": rating,
                    "solved": solved
                }
            
            self.logger.info(f"Prepared data for {len(self.participants_data)} participants")
            return True
        except Exception as e:
            self.logger.error(f"Error preparing renderer data: {str(e)}")
            return False
        
    def process_web(self):
        result = {}
        try:
            if not self.participants_data:
                self.logger.warning("No participants data available. Call prepare() first.")
                return {}
            
            for handle, data in self.participants_data.items():
                name = data.get("name", "")
                rating = data.get("rating", 0)
                solved = data.get("solved", 0)
                
                # Calculate score using the new formula
                normalized_rating = rating / self.MAX_RATING
                normalized_solved = solved / self.MAX_SOLVED if self.MAX_SOLVED > 0 else 0
                score = 500 * (normalized_rating + normalized_solved)
                
                if self.mode == 'short':
                    result[handle] = [name, round(score)]
                elif self.mode == 'full':
                    result[handle] = {'name': name, 'cf_score': round(500 * normalized_rating, 1), 'informatics_score': round(500 * normalized_solved, 1), 'score': round(score)}
            
            self.logger.info(f"Processed scores for {len(result)} participants")
            return result
        except Exception as e:
            self.logger.error(f"Error processing renderer data: {str(e)}")
            return {}
        
    def process_dump(self):
        return self.participants_data
    
    def process(self):
        """
        Process the prepared data and return an object with the structure:
        {
            handle: [name, score]
        }
        
        Score is calculated as:
        500 * (rating / MAX_RATING + solved / MAX_SOLVED)
        
        Where:
        - MAX_RATING = 2000
        - MAX_SOLVED = total number of problems across all contests
        
        Returns:
            dict: Dictionary mapping handles to lists with name and calculated score
        """
        result = {}
        if self.mode in ['short', 'full']:
            result = self.process_web()
        elif self.mode in ['dumper']:
            result = self.process_dump()
        return result
        
        

