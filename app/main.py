import sys
import os

# 获取项目根目录的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 现在可以正确导入app包下的模块
from app.utils.logger import LogSetup
from app.utils.mutex import AppMutex
from app.gui.main_window import MainWindow
import tkinter as tk  # 补充导入tkinter

def main():
    # 初始化日志系统
    LogSetup.initialize()
    
    # 检查单例运行
    mutex = AppMutex()
    if not mutex.acquire():
        tk.messagebox.showinfo("提示", "程序已在运行")
        return

    # 创建主界面
    app = MainWindow()
    app.mainloop()

    # 释放资源
    mutex.release()

if __name__ == "__main__":
    main()