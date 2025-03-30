import win32api
import win32event
import winerror
import sys
import pywintypes
import logging

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

def show_window(self, icon=None, item=None):
        """从托盘恢复窗口"""
        if icon:  # 如果提供了icon参数
            icon.stop()  # 停止托盘图标
        self.master.deiconify()  # 显示窗口
        self.setup_ui()  # 重新设置或刷新UI界面

def hide_window(self):
    """隐藏窗口并显示托盘图标"""
    self.master.withdraw()  # 隐藏窗口

    def setup_system_tray():  # 设置系统托盘
        # 加载托盘图标
        icon_image = Image.open("./icons/ECUT.ico")

        # 创建托盘图标
        self.icon = pystray.Icon(
            "campus_net_login",  # 托盘图标的名称
            icon=icon_image,  # 托盘图标的图像
            title="校园网自动登录",  # 托盘图标的标题
            menu=pystray.Menu(
                item("打开", self.show_window, default=True),
                item("退出", lambda icon, item: self.quit_app(icon)),
            ),  # 托盘图标的菜单
        )
        # 运行托盘图标
        self.icon.run_detached()

    # 在后台线程中设置系统托盘，防止阻塞主线程
    threading.Thread(target=setup_system_tray).start()

def quit_app(self, icon=None, item=None):  # 退出应用
    if icon:  # 如果提供了icon参数
        icon.stop()  # 停止托盘图标
    # 保存配置，清理资源，退出程序的其余步骤
    self.master.quit()
    # 可能有必要的清理步骤
    self.master.destroy()

def on_main_close(root, settings_manager):  # 主窗口关闭事件处理函数
    global mutex, mutex_created  # 声明全局变量mutex和mutex_created
    if messagebox.askokcancel(
        "退出", "确定要退出应用吗？"
    ):  # 弹出确认对话框，用户确认退出应用
        settings_manager.save_config_to_disk()  # 确保退出前保存配置到磁盘
        root.destroy()  # 销毁主窗口，退出应用
        if mutex and mutex_created:  # 如果互斥锁存在且已创建
            win32event.ReleaseMutex(mutex)  # 释放互斥锁
            win32api.CloseHandle(mutex)  # 关闭互斥锁的句柄
            mutex_created = False  # 重置互斥锁创建标志
