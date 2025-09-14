import cloudscraper
from bs4 import BeautifulSoup
import os
import logging
from dotenv import load_dotenv
from lib.global_data import GlobalData


class InformaticsSessionReanimator(object):
    def __init__(self) -> None:
        self.url = 'https://informatics.msk.ru/'
        self.login_url = self.url + 'login/index.php'
        self.logger = logging.getLogger(__name__)
        self.username = None
        self.password = None
        self.INFORMATICS_DIR = None
        self.PROJECT_ROOT = None

    def prepare(self) -> bool:
        """Reads environment variables needed for authentication
        """
        load_dotenv()
        try:
            self.username = os.environ.get('INFORMATICS_USERNAME')
            self.password = os.environ.get('INFORMATICS_PASSWORD')
            self.INFORMATICS_DIR = os.environ.get('INFORMATICS_DIR')
            self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
            
            # Check if all required environment variables are set
            if not all([self.username, self.password, self.INFORMATICS_DIR, self.PROJECT_ROOT]):
                self.logger.error("Missing required environment variables for Informatics authentication")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error reading environment variables: {str(e)}")
            return False

    def process(self) -> bool:
        """Authenticates with Informatics and stores the session in GlobalData
        """
            
        try:
            # Create a new session
            session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            # Get the login page
            self.logger.info("Получение страницы логина...")
            form = session.get(self.login_url)
            
            # Check response status
            if form.status_code != 200:
                self.logger.info(f"Ошибка при получении страницы логина. Статус: {form.status_code}")
                return False
                
            # Parse HTML to extract token
            soup = BeautifulSoup(form.text, 'html.parser')
            
            # Find login form
            login_form = soup.find('form', {'id': 'login'})
            
            # Get action URL from form if it exists
            form_action = login_form.get('action')
            login_url = form_action if form_action else self.login_url
            
            # If action URL is relative, convert it to absolute
            if form_action and not form_action.startswith('http'):
                if form_action.startswith('/'):
                    login_url = self.url.rstrip('/') + form_action
                else:
                    login_url = self.url + form_action
            
            # Find all hidden fields in the login form
            hidden_inputs = login_form.find_all('input', {'type': 'hidden'})
            login_data = {
                'anchor': '',
                'username': self.username,
                'password': self.password,
                'rememberusername': 1
            }
            
            # Add all hidden fields to the data to be sent
            for input_field in hidden_inputs:
                if 'name' in input_field.attrs and 'value' in input_field.attrs:
                    login_data[input_field.attrs['name']] = input_field.attrs['value']

            # Send authentication request
            res = session.post(login_url, data=login_data)
            
            # Check if login was successful
            login_successful = 'Вы зашли под именем' in res.text
            
            if login_successful:
                # Store the session in GlobalData
                GlobalData().set_informatics_session(session)
                self.logger.info("Успешная авторизация и сохранение сессии")
                return True
            else:
                self.logger.error("Ошибка авторизации: неверные учетные данные или изменился формат страницы")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при авторизации: {str(e)}")
            return False