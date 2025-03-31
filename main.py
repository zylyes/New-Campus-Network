

# 用于缓存配置的全局变量
cached_config = {}

setup_logging()  # 调用日志设置函数

config_lock = threading.Lock()  # 创建一个线程锁

if __name__ == "__main__":  # 如果当前脚本被直接运行
    # 尝试创建一个互斥锁
    mutex = win32event.CreateMutex(
        None, True, "Global\\CampusNetLoginAppMutex"
    )  # 创建一个互斥锁
    last_error = win32api.GetLastError()  # 获取最后一个错误

    if last_error == winerror.ERROR_ALREADY_EXISTS:  # 如果互斥锁已经存在
        messagebox.showinfo("校园网自动登录", "应用程序已在运行。")  # 弹出信息提示框
        sys.exit(0)  # 退出程序
    else:  # 如果互斥锁不存在
        mutex_created = True  # 设置互斥锁创建标志为True

    root = tk.Tk()  # 创建一个Tkinter的根窗口对象
    root.withdraw()  # 隐藏根窗口，不显示在屏幕上

    # 创建设置管理器实例
    settings_manager = CampusNetSettingsManager()
    # 创建应用程序实例
    app = CampusNetLoginApp(root, settings_manager=settings_manager, show_ui=True)

    # 传递 settings_manager 实例到关闭函数
    root.protocol("WM_DELETE_WINDOW", lambda: on_main_close(root, settings_manager))

    if app.show_ui:  # 如果需要显示UI界面
        root.deiconify()  # 显示根窗口

    root.mainloop()  # 进入Tkinter的主事件循环，等待用户交互```

    # 程序退出时，确保释放资源
    if mutex_created:  # 如果互斥锁已经创建
        win32event.ReleaseMutex(mutex)  # 释放互斥锁
        win32api.CloseHandle(mutex)  # 关闭互斥锁
        mutex_created = False  # 重置互斥锁创建标志为False
