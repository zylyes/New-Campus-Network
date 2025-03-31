# 互斥锁管理器
from tkinter import messagebox # 从tkinter导入messagebox和ttk，用于图形界面中的对话框和高级组件
import os  # 导入os库，用于处理操作系统级别的接口，如文件管理
import logging  # 导入logging库，用于记录日志
import subprocess  # 导入subprocess库，用于调用外部进程
import threading  # 导入threading库，用于多线程编程
import time  # 导入time库，用于时间操作
import win32api  # 导入win32api库，用于Windows API操作
import winshell  # 导入winshell库用于Windows快捷方式操作
import pywintypes  # 导入pywintypes库，用于Windows API操作
import win32event  # 导入win32event模块，用于Windows事件操作
import winerror  # 导入winerror模块，用于Windows错误码
import sys  # 导入sys库，用于系统相关的操作
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

def apply_auto_start_setting(self):  # 应用自动启动设置
    start_up_folder = winshell.startup()  # 获取Windows启动文件夹路径
    shortcut_path = os.path.join(
        start_up_folder, "CampusNetLoginApp.lnk"
    )  # 设置快捷方式路径和文件名
    if self.config.get("auto_start"):  # 检查配置中是否开启了自动启动
        if not os.path.exists(shortcut_path):  # 如果快捷方式不存在
            # 使用winshell创建快捷方式
            script_path = os.path.join(
                os.getcwd(), "校园网登录程序.exe"
            )  # 设置可执行文件的路径
            with winshell.shortcut(shortcut_path) as shortcut:  # 创建快捷方式
                shortcut.path = script_path  # 设置快捷方式的目标路径
                shortcut.description = "自动登录校园网的应用"  # 设置快捷方式描述
                shortcut.working_directory = os.getcwd()  # 设置工作目录为当前目录
    else:  # 如果配置中未开启自动启动
        if os.path.exists(shortcut_path):  # 如果快捷方式存在
            # 删除快捷方式
            os.remove(shortcut_path)

def restart_app(self):  # 重启应用程序
    def restart():  # 重启逻辑
        # 等待一小段时间，确保主进程有足够的时间退出
        time.sleep(1)
        # 使用subprocess启动新的应用实例
        subprocess.Popen(["校园网登录程序.exe"])
        # 退出当前应用
        self.master.quit()

    # 在后台线程中执行重启逻辑，以避免阻塞UI或其他处理
    threading.Thread(target=restart).start()


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
