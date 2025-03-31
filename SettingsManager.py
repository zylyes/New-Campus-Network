
# 配置管理类
class SettingsManager:
    def __init__(self, config_file="config.json", default_config=None):  # 初始化方法
        self.config_lock = threading.Lock()  # 创建一个线程锁
        self.cached_config = {}  # 创建一个缓存配置的字典
        self.config_file = config_file  # 配置文件名
        self.default_config = {  # 默认配置
            "api_url": "http://172.21.255.105:801/eportal/",  # API URL
            "icons": {  # 图标
                "already": "./icons/Internet.ico",  # 已登录
                "success": "./icons/Check.ico",  # 成功
                "fail": "./icons/Cross.ico",  # 失败
                "unknown": "./icons/Questionmark.ico",  # 未知
            },
            "minimize_to_tray_on_login": True,  # 默认情况下登录成功后最小化到托盘
            "auto_login": False,  # 默认情况下不自动登录
            "isp": "campus",  # 默认运营商为校园网
            "auto_start": False,  # 默认情况下不自动启动
        }

    def load_or_create_config(self):  # 加载或创建配置
        if self.cached_config:  # 如果缓存配置存在
            return self.cached_config  # 直接返回缓存配置

        logging.debug("尝试加载配置文件...")  # 记录调试信息：尝试加载配置文件

        with self.config_lock:  # 使用线程锁
            if not os.path.exists(self.config_file):  # 如果配置文件不存在
                logging.info(
                    "配置文件不存在，创建默认配置文件。"
                )  # 记录信息：配置文件不存在，创建默认配置文件
                with open(
                    self.config_file, "w"
                ) as config_file:  # 以写入模式打开配置文件
                    json.dump(
                        self.default_config, config_file
                    )  # 将默认配置写入配置文件
            else:  # 如果配置文件存在
                logging.info("配置文件加载成功。")  # 记录信息：配置文件加载成功
            with open(self.config_file, "r") as config_file:  # 以只读模式打开配置文件
                self.cached_config = json.load(config_file)  # 加载配置文件到缓存配置

        return self.cached_config  # 返回缓存配置

    def save_config_to_disk(self):  # 保存配置到磁盘
        logging.debug("保存配置到文件中...")  # 记录调试信息：保存配置到文件中
        with self.config_lock:  # 使用线程锁
            with open(self.config_file, "w") as config_file:  # 以写入模式打开配置文件
                json.dump(self.cached_config, config_file)  # 将缓存配置保存到配置文件
        logging.info("配置已保存到磁盘")  # 记录信息：配置已保存到磁盘

    def save_config(self, config):  # 保存配置
        self.cached_config.update(config)  # 更新缓存配置
        logging.info("配置已更新到缓存")  # 记录信息：配置已更新到缓存

    