import json
import threading
import os

class CampusNetSettingsManager:  
    def __init__(self, config_file="config.json"):  
        self.config_lock = threading.Lock()  
        self.cached_config = {}  
        self.config_file = config_file  
        self.default_config = {  
            "api_url": "http://172.21.255.105:801/eportal/",  
            "icons": {  
                "already": "./icons/Internet.ico",  
                "success": "./icons/Check.ico",  
                "fail": "./icons/Cross.ico",  
                "unknown": "./icons/Questionmark.ico",  
            },
            "minimize_to_tray_on_login": True,  
            "auto_login": False,  
            "isp": "campus",  
            "auto_start": False,  
        }

    CURRENT_VERSION = "1.4.2"

    def load_or_create_config(self):  
        if self.cached_config:  
            return self.cached_config  

        with self.config_lock:  
            if not os.path.exists(self.config_file):  
                with open(self.config_file, "w") as config_file:  
                    json.dump(self.default_config, config_file)  
            else:  
                with open(self.config_file, "r") as config_file:  
                    self.cached_config = json.load(config_file)  

        return self.cached_config  

    def save_config_to_disk(self):  
        with self.config_lock:  
            with open(self.config_file, "w") as config_file:  
                json.dump(self.cached_config, config_file)