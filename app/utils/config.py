import json
import os
import logging
from threading import Lock
from packaging import version

class ConfigManager:
    _instance = None
    _lock = Lock()
    CONFIG_VERSION = "1.4.2"

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.config_file = "config.json"
        self.default_config = {
            "version": self.CONFIG_VERSION,
            "api_url": "http://172.21.255.105:801/eportal/",
            "auto_login": False,
            "minimize_to_tray": True,
            "auto_start": False
        }
        self.config = self._load_config()
        self._migrate_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
            return self.default_config.copy()
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            return self.default_config.copy()

    def _migrate_config(self):
        current_ver = version.parse(self.CONFIG_VERSION)
        config_ver = version.parse(self.config.get("version", "1.0.0"))
        
        if config_ver < version.parse("1.4.0"):
            logging.info("Migrating config from version <1.4.0")
            self.config.setdefault("minimize_to_tray", True)
        
        self.config["version"] = self.CONFIG_VERSION

    def save(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logging.info("Config saved successfully")
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")

    def __getitem__(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        self.config[key] = value