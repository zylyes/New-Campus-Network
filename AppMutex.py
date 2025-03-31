
# 互斥锁管理类
class AppMutex:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.mutex = None
            cls.mutex_created = False
        return cls._instance
    
    def create(self):
        try:
            # 正确传递三个参数
            self.mutex = win32event.CreateMutex(
                None,           # 安全属性
                True,           # 立即拥有
                "Global\\CampusNetLoginAppMutex"  # 唯一名称
            )
            last_error = win32api.GetLastError()
            
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                print("程序已在运行")
                self.cleanup()
                sys.exit(0)
            else:
                self.mutex_created = True
                print("互斥锁创建成功")
                
        except pywintypes.error as e:
            if e.winerror == winerror.ERROR_ACCESS_DENIED:
                logging.error("权限不足，无法创建互斥锁")
            else:
                logging.error(f"系统错误: {e.strerror} (代码 {e.winerror})")
 
    def cleanup(self):
        if self.mutex_created and self.mutex:
            win32event.ReleaseMutex(self.mutex)
            win32api.CloseHandle(self.mutex)
            self.mutex_created = False
            print("互斥锁已释放")