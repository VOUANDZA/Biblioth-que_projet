import json
import os
from pathlib import Path

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config_dir = Path('config')
        self.config_file = self.config_dir / 'config.json'
        self.default_config = {
            'theme': 'light',
            'session_duration': 7200,  # 2 hours in seconds
            'max_login_attempts': 3,
            'log_level': 'INFO',
            'db_file': 'bibliotheque.db',
            'secret_key': 'your-secret-key-change-this'
        }
        self._load_config()
    
    def _load_config(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        if not self.config_file.exists():
            self.config = self.default_config
            self._save_config()
        else:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self._save_config() 