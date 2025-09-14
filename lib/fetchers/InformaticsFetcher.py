import os
import pathlib
import logging
from dotenv import load_dotenv
from lib.global_data import GlobalData
from lib.fetchers.InformaticsSessionReanimator import InformaticsSessionReanimator


class InformaticsFetcher(object):
    def __init__(self) -> None:
        self.url = 'https://informatics.msk.ru/'
        self.login_url = self.url + 'login/index.php'
        self.standings_url = self.url + 'py/monitor?contest_id={}'
        self.logger = logging.getLogger(__name__)


    def prepare(self) -> bool:
        """Get session from GlobalData or create a new one using InformaticsSessionReanimator
        """
        load_dotenv()
        try:
            # Read environment variables
            self.INFORMATICS_DIR = os.environ.get('INFORMATICS_DIR')
            self.PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
            
            # If no session exists, use InformaticsSessionReanimator to create one
            if GlobalData().get_informatics_session() is None:
                self.logger.info("No existing session found, creating a new one...")
                reanimator = InformaticsSessionReanimator()
                if not reanimator.prepare():
                    self.logger.error("Failed to prepare InformaticsSessionReanimator")
                    return False
                    
                if not reanimator.process():
                    self.logger.error("Failed to create a new session")
                    return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error in prepare: {str(e)}")
            return False

    def process(self):
        """Load and save contests data
        """
        # Получаем список ID контестов из переменной окружения
        contest_ids_str = os.environ.get('INFORMATICS_CONTEST_IDS')

        contest_ids = [id.strip() for id in contest_ids_str.split(',')]
        
        # Создаем директорию для сохранения результатов, если она не существует
        save_dir = pathlib.Path(os.path.join(self.PROJECT_ROOT, self.INFORMATICS_DIR))
        save_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for contest_id in contest_ids:
            self.logger.info(f"Загрузка результатов для контеста {contest_id}...")
            try:
                # Получаем страницу с результатами
                response = GlobalData().get_informatics_session().get(self.standings_url.format(contest_id))
                
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
