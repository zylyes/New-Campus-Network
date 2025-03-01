import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LogSetup:
    class PasswordFilter(logging.Filter):
        def filter(self, record):
            if "user_password=" in record.getMessage():
                record.msg = record.msg.replace(
                    record.msg.split("user_password=")[1].split("&")[0], "********"
                )
                record.args = ()
            return True

    @classmethod
    def initialize(cls):
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # 确保日志目录存在
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 主logger配置
        logger = logging.getLogger()
        logger.setLevel(log_level)
        
        # 文件处理器
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            when="midnight",
            backupCount=7
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.addFilter(cls.PasswordFilter())
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        console_handler.addFilter(cls.PasswordFilter())
        logger.addHandler(console_handler)