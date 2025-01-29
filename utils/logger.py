import logging
from datetime import datetime
import os

class LibraryLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LibraryLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        self.logger = logging.getLogger('library')
        self.logger.setLevel(logging.INFO)
        
        # Créer le dossier logs s'il n'existe pas
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Log file handler
        file_handler = logging.FileHandler(
            f'logs/library_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_action(self, action_type, user_id, details):
        self.logger.info({
            'action': action_type,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })
    
    def log_error(self, error_type, user_id, error_details):
        self.logger.error({
            'error': error_type,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'details': error_details
        }) 