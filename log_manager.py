# 日志管理器
import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 定义一个自定义的日志过滤器类PasswordFilter
class PasswordFilter(logging.Filter):  # 继承logging.Filter类
    def filter(self, record):  # 定义过滤器方法
        message = record.getMessage()  # 获取日志记录的消息
        if "user_password=" in message:  # 如果日志信息中包含'user_password='
            new_message = message.replace(
                message.split("user_password=")[1].split("&")[0], "********"
            )  # 将密码部分替换为'********'
            record.msg = new_message  # 更新日志记录的消息
            record.args = ()  # 清空args以避免格式化错误
        return True  # 返回True以允许记录消息

# 用于缓存配置的全局变量
cached_config = {}

def setup_logging():
    """根据环境变量设置日志记录器的配置"""
    # 获取日志级别，默认为DEBUG
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    # 设置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 确保日志目录存在
    log_directory = "logs"  # 日志文件夹名称
    if not os.path.exists(log_directory):  # 如果日志目录不存在
        os.makedirs(log_directory)  # 创建日志目录

    # 创建日志记录器
    logger = logging.getLogger()  # 获取全局日志记录器对象
    logger.setLevel(log_level)  # 设置日志记录器的日志级别

    # 创建TimedRotatingFileHandler处理程序，每天生成一个新日志文件，最多保留7个日志文件
    log_file_path = os.path.join(
        log_directory, "campus_net_login_app.log"
    )  # 将日志文件放在logs目录下
    handler = TimedRotatingFileHandler(
        log_file_path, when="midnight", interval=1, backupCount=7
    )  # 创建按时间滚动的文件处理程序

    # 设置日志格式
    formatter = logging.Formatter(log_format)  # 创建日志格式对象
    handler.setFormatter(formatter)  # 将格式应用到handler
    logger.addHandler(handler)  # 将handler添加到logger以记录日志信息

    # 控制台输出
    console_handler = logging.StreamHandler()  # 创建控制台输出handler
    console_handler.setFormatter(formatter)  # 设置控制台输出的日志格式
    logger.addHandler(console_handler)  # 将控制台输出handler添加到logger中

    # 创建日志过滤器并添加到handler
    pwd_filter = PasswordFilter()  # 创建密码过滤器对象
    handler.addFilter(pwd_filter)  # 将密码过滤器添加到文件输出handler
    console_handler.addFilter(pwd_filter)  # 将密码过滤器添加到控制台输出handler

    # 隐藏PIL的DEBUG日志消息
    pil_logger = logging.getLogger("PIL")  # 获取PIL模块的日志记录器
    pil_logger.setLevel(
        logging.INFO
    )  # 将PIL的日志级别设置为INFO，这样就不会显示DEBUG消息
