import logging

class GlobalData:
    """
    Singleton class to store global data from parsers.
    
    This class stores:
    - users_data: Dictionary mapping handles to dictionaries with name and rating from UsersParser
    - informatics_data: Dictionary mapping participant names to lists of solved problems from InformaticsParser
    - informatics_common_data: List containing the number of problems in each contest
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalData, cls).__new__(cls)
            cls._instance.users_data = {}
            cls._instance.informatics_data = {}
            cls._instance.informatics_common_data = []
            cls._instance.informatics_session = None
            cls._instance.logger = logging.getLogger(__name__)
        return cls._instance
    
    def update_users_data(self, data):
        """
        Update the users data.
        
        Args:
            data (dict): Dictionary mapping handles to dictionaries with name and rating
        """
        if not isinstance(data, dict):
            self.logger.error("Invalid users data format. Expected dictionary.")
            return
            
        self.users_data = data
        self.logger.info(f"Updated users data with {len(data)} entries")
    
    def update_informatics_data(self, data):
        """
        Update the informatics data.
        
        Args:
            data (dict): Dictionary mapping participant names to lists of solved problems
        """
        if not isinstance(data, dict):
            self.logger.error("Invalid informatics data format. Expected dictionary.")
            return
            
        self.informatics_data = data
        self.logger.info(f"Updated informatics data with {len(data)} entries")
    
    def update_informatics_common_data(self, data):
        """
        Update the informatics common data.
        
        Args:
            data (list): List containing the number of problems in each contest
        """
        if not isinstance(data, list):
            self.logger.error("Invalid informatics common data format. Expected list.")
            return
            
        self.informatics_common_data = data
        self.logger.info(f"Updated informatics common data with {len(data)} contests")
    
    def get_users_data(self):
        """
        Get the users data.
        
        Returns:
            dict: Dictionary mapping handles to dictionaries with name and rating
        """
        return self.users_data
    
    def get_informatics_data(self):
        """
        Get the informatics data.
        
        Returns:
            dict: Dictionary mapping participant names to lists of solved problems
        """
        return self.informatics_data
    
    def get_informatics_common_data(self):
        """
        Get the informatics common data.
        
        Returns:
            list: List containing the number of problems in each contest
        """
        return self.informatics_common_data
        
    def set_informatics_session(self, session):
        """
        Set the informatics session.
        
        Args:
            session: The cloudscraper session object
        """
        self.informatics_session = session
        self.logger.info("Updated informatics session")
        
    def get_informatics_session(self):
        """
        Get the informatics session.
        
        Returns:
            The cloudscraper session object or None if not set
        """
        return self.informatics_session