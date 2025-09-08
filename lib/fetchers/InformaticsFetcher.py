import cloudscraper
from bs4 import BeautifulSoup
import os
import pathlib
import logging
from dotenv import load_dotenv


class InformaticsFetcher(object):
    def __init__(self) -> None:
        self.url = 'https://informatics.msk.ru/'
        self.login_url = self.url + 'login/index.php'
        self.standings_url = self.url + 'py/monitor?contest_id={}'
        self.logger = logging.getLogger(__name__)


    def prepare(self) -> bool:
        """Authorises user
        """
        load_dotenv()
        try:
            username = os.environ.get('INFORMATICS_USERNAME', '')
            password = os.environ.get('INFORMATICS_PASSWORD', '')
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            # Получаем страницу логина с помощью cloudscraper
            self.logger.info("Получение страницы логина...")
            form = self.session.get(self.login_url)
            
            # Проверяем статус ответа
            if form.status_code != 200:
                self.logger.info(f"Ошибка при получении страницы логина. Статус: {form.status_code}")
                return False
                
            # Парсим HTML для извлечения токена
            soup = BeautifulSoup(form.text, 'html.parser')
            
            # Ищем форму логина
            login_form = soup.find('form', {'id': 'login'})
            
            # Получаем action URL из формы, если он есть
            form_action = login_form.get('action')
            login_url = form_action if form_action else self.login_url
            
            # Если action URL относительный, преобразуем его в абсолютный
            if form_action and not form_action.startswith('http'):
                if form_action.startswith('/'):
                    login_url = self.url.rstrip('/') + form_action
                else:
                    login_url = self.url + form_action
            
            # Ищем все скрытые поля в форме логина
            hidden_inputs = login_form.find_all('input', {'type': 'hidden'})
            login_data = {
                'anchor': '',
                'username': username,
                'password': password,
                'rememberusername': 1
            }
            
            # Добавляем все скрытые поля в данные для отправки
            for input_field in hidden_inputs:
                if 'name' in input_field.attrs and 'value' in input_field.attrs:
                    login_data[input_field.attrs['name']] = input_field.attrs['value']

            # Отправляем запрос на авторизацию
            res = self.session.post(login_url, data=login_data)

            return 'Вы зашли под именем' in res.text
            
        except Exception as e:
            print(f"Ошибка при авторизации: {str(e)}")
            return False

    def process(self):
        """Load and save contests data
        """
        # Получаем список ID контестов из переменной окружения
        contest_ids_str = os.environ.get('INFORMATICS_CONTEST_IDS', '')

        contest_ids = [id.strip() for id in contest_ids_str.split(',')]
        
        # Создаем директорию raw/informatics, если она не существует
        save_dir = pathlib.Path('raw/informatics')
        save_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for contest_id in contest_ids:
            self.logger.info(f"Загрузка результатов для контеста {contest_id}...")
            try:
                # Получаем страницу с результатами
                response = self.session.get(self.standings_url.format(contest_id))
                
                if response.status_code != 200:
                    self.logger.info(f"Ошибка при получении результатов для контеста {contest_id}. Статус: {response.status_code}")
                    continue
                
                # Сохраняем HTML-ответ в файл
                file_path = save_dir / f"contest_{contest_id}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                self.logger.info(f"Результаты для контеста {contest_id} сохранены в {file_path}")
                results[contest_id] = response
                
            except Exception as e:
                self.logger.info(f"Ошибка при обработке контеста {contest_id}: {str(e)}")
        
        return results




