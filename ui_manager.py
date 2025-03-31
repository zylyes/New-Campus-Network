# UI管理器
import tkinter as tk  # 导入tkinter库，用于GUI界面创建
from tkinter import (
    messagebox,
    ttk,
)  # 从tkinter导入messagebox和ttk，用于图形界面中的对话框和高级组件
from config_manager import load_credentials  # 导入加载凭据的函数

def center_window(self, width=300, height=200):
    """将窗口置于屏幕中央"""
    # 获取屏幕宽度和高度
    screen_width = self.master.winfo_screenwidth()
    screen_height = self.master.winfo_screenheight()

    # 计算窗口在屏幕中央的位置
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口的几何尺寸和位置
    self.master.geometry(f"{width}x{height}+{x}+{y}")

def toggle_password_visibility(password_entry, toggle_button, eye_closed_icon, eye_open_icon, password_visible):
    """
    切换密码框中的密码可见性，并更新切换按钮的图标
    """
    if password_visible[0]:
        # 如果密码可见，则将密码框中的字符显示为'*'
        password_entry.config(show="*")
        # 更新切换密码可见性按钮的图标为关闭眼睛图标
        toggle_button.config(image=eye_closed_icon)
        # 更新密码可见性标志为False，密码不可见
        password_visible[0] = False
    else:
        # 如果密码不可见，则将密码框中的字符显示为原文
        password_entry.config(show="")
        # 更新切换密码可见性按钮的图标为打开眼睛图标
        toggle_button.config(image=eye_open_icon)
        # 更新密码可见性标志为True，密码可见
        password_visible[0] = True

def open_settings(master, config, center_window_on_parent, clear_key_and_credentials, clear_credentials, on_settings_close, save_settings_and_close):
    """
    打开设置窗口
    """
    master.withdraw()  # 隐藏主窗口
    settings_window = tk.Toplevel(master)  # 创建设置窗口
    settings_window.title("设置")  # 设置窗口标题
    settings_window.resizable(False, False)  # 禁止调整窗口大小
    center_window_on_parent(settings_window, 300, 212)  # 调整窗口位置和大小

    minimize_to_tray_var = tk.IntVar(value=config.get("minimize_to_tray_on_login", True))
    auto_start_var = tk.IntVar(value=config.get("auto_start", False))
    auto_login_var = tk.IntVar(value=config.get("auto_login", False))

    main_frame = ttk.Frame(settings_window)
    main_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="API URL：").grid(row=0, column=0, pady=(0, 10), sticky="w")
    api_url_entry = ttk.Entry(main_frame)
    api_url_entry.grid(row=0, column=1, pady=(0, 10), sticky="ew")
    api_url_entry.insert(0, config.get("api_url", ""))

    ttk.Checkbutton(main_frame, text="登录成功后最小化到托盘", variable=minimize_to_tray_var).grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="w")
    ttk.Checkbutton(main_frame, text="开机时自动启动", variable=auto_start_var).grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="w")
    ttk.Checkbutton(main_frame, text="自动登录", variable=auto_login_var).grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky="w")

    ttk.Button(main_frame, text="清除密钥和用户凭证", command=clear_key_and_credentials).grid(row=4, column=0, pady=(10, 0), sticky="ew")
    ttk.Button(main_frame, text="清除用户凭证", command=clear_credentials).grid(row=4, column=1, pady=(10, 0), sticky="ew")

    ttk.Button(main_frame, text="取消", command=lambda: on_settings_close(settings_window)).grid(row=5, column=1, pady=(10, 0), sticky="e")
    ttk.Button(main_frame, text="保存", command=lambda: save_settings_and_close(api_url_entry.get(), settings_window, config, minimize_to_tray_var, auto_start_var, auto_login_var)).grid(row=5, column=0, pady=(10, 0), sticky="w")

    main_frame.grid_columnconfigure(1, weight=1)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: on_settings_close(settings_window))

def setup_ui(self):  # 移除center_window参数
    self.master.title("校园网自动登录")  # 设置窗口标题
    center_window(self, width=296, height=228)  # 调用center_window函数

    main_frame = ttk.Frame(self.master)  # 创建一个新的框架
    main_frame.pack(
        padx=10, pady=10, expand=True, fill=tk.BOTH
    )  # 将框架放置在窗口中

    ttk.Label(main_frame, text="用户名：", anchor="w").grid(
        row=0, column=0, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加标签
    self.username_entry = ttk.Entry(main_frame)  # 创建一个输入框
    self.username_entry.grid(
        row=0, column=1, padx=5, pady=5, sticky="ew"
    )  # 将输入框放置在框架中

    ttk.Label(main_frame, text="密码：", anchor="w").grid(
        row=1, column=0, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加标签
    self.password_entry = ttk.Entry(main_frame, show="*")  # 创建一个密码输入框
    self.password_entry.grid(
        row=1, column=1, padx=5, pady=5, sticky="ew"
    )  # 将密码输入框放置在框架中

    self.password_visible = [False]  # 使用列表包装布尔值以便在函数中修改
    self.toggle_password_btn = tk.Button(
        main_frame,
        image=self.eye_closed_icon,
        command=lambda: toggle_password_visibility(
            self.password_entry,
            self.toggle_password_btn,
            self.eye_closed_icon,
            self.eye_open_icon,
            self.password_visible,
        ),
        borderwidth=0,
    )  # 创建一个按钮
    self.toggle_password_btn.grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )  # 将按钮放置在框架中

    self.remember_var = tk.IntVar()  # 创建一个整型变量
    ttk.Checkbutton(
        main_frame, text="记住账号和密码", variable=self.remember_var
    ).grid(
        row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w"
    )  # 在框架中添加复选框

    self.isp_combobox = ttk.Combobox(
        main_frame, textvariable=self.isp_var, state="readonly", width=12
    )  # 创建一个下拉框
    self.isp_combobox["values"] = (
        "中国电信",
        "中国移动",
        "中国联通",
        "校园网",
    )  # 设置下拉框的选项
    self.isp_combobox.grid(
        row=2, column=1, columnspan=2, padx=5, pady=5, sticky="e"
    )  # 将下拉框放置在框架中

    # 登录按钮
    ttk.Button(main_frame, text="登录", command=self.login).grid(
        row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加按钮

    # 设置按钮
    ttk.Button(main_frame, text="设置", command=lambda: open_settings(
        self.master,
        self.config,
        self.center_window_on_parent,
        self.clear_key_and_credentials,
        self.clear_credentials,
        self.on_settings_close,
        self.save_settings_and_close
    )).grid(
        row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加按钮

    # 报告问题和提交建议按钮
    ttk.Button(main_frame, text="报告问题", command=self.report_error).grid(
        row=5, column=0, columnspan=1, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加按钮
    ttk.Button(main_frame, text="提交建议", command=self.open_suggestion_box).grid(
        row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew"
    )  # 在框架中添加按钮

    # 加载保存的用户名和密码，如果设置了记住我
    username, password, isp, remember = load_credentials(self.config)  # 调用加载凭据函数
    if username and password and remember:  # 如果用户名和密码存在且记住密码
        self.username_entry.insert(0, username)  # 在用户名输入框中插入用户名
        self.password_entry.insert(0, password)  # 在密码输入框中插入密码
        self.isp_combobox.set(isp)  # 设置运营商下拉框
        self.remember_var.set(1)  # 设置记住密码复选框为选中状态

    # 配置列权重
    main_frame.columnconfigure(1, weight=1)  # 第二列应在需要时扩展
    main_frame.columnconfigure(
        0, minsize=70
    )  # 第一列设置最小宽度，确保标签不会被压缩

    self.master.update()  # 更新主窗口，以便下面的代码能获取到最新的尺寸信息

    report_button = ttk.Button(
        main_frame, text="报告问题", command=self.report_error
    )  # 创建报告问题按钮
    suggest_button = ttk.Button(
        main_frame, text="提交建议", command=self.open_suggestion_box
    )  # 创建提交建议按钮
    report_button.grid(
        row=5, column=0, padx=5, pady=5, sticky="ew"
    )  # 报告问题按钮放置在框架中
    suggest_button.grid(
        row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew"
    )  # 提交建议按钮放置在框架中

    # 设置按钮让它们在同一行中拥有相同的宽度
    main_frame.grid_columnconfigure(0, weight=1)  # 报告问题按钮占据列宽
    main_frame.grid_columnconfigure(1, weight=1)  # 提交建议按钮占据列宽
    main_frame.grid_columnconfigure(
        2, weight=1
    )  # 保持第三列扩展能力，使所有列均匀分配空间

    # 如果窗口过大（比如在高DPI屏幕上），设置合适的窗口尺寸和位置
    current_width = self.master.winfo_width()  # 获取当前窗口宽度
    current_height = self.master.winfo_height()  # 获取当前窗口高度
    screen_width = self.master.winfo_screenwidth()  # 获取屏幕宽度
    screen_height = self.master.winfo_screenheight()  # 获取屏幕高度

    if current_width > screen_width or current_height > screen_height:
        # 如果窗口比屏幕尺寸大，重新调整大小
        scaled_width = int(current_width * 0.9)  # 缩小窗口宽度
        scaled_height = int(current_height * 0.9)  # 缩小窗口高度
        center_window(
            self, width=scaled_width, height=scaled_height
        )  # 调用传入的center_window函数

def save_settings_and_close(self, api_url, settings_window):  # 保存设置并关闭
    # 弹出确认保存设置对话框
    confirm = messagebox.askyesno("确认保存设置", "您确定要保存这些设置吗？")
    if confirm:  # 如果用户选择确认
        # 更新程序的配置实例
        self.config["api_url"] = api_url  # 更新API URL
        self.config["minimize_to_tray_on_login"] = (
            self.minimize_to_tray_var.get()
        )  # 更新最小化到托盘设置
        self.config["auto_start"] = self.auto_start_var.get()  # 更新自动启动设置
        self.config["auto_login"] = self.auto_login_var.get()  # 更新自动登录设置

        # 保存配置到管理器和磁盘
        self.settings_manager.save_config(self.config)  # 保存配置到管理器
        self.settings_manager.save_config_to_disk()  # 保存配置到磁盘

        # 更新启动时自动启动设置
        self.apply_auto_start_setting()

        # 显示已保存配置的消息，并关闭设置窗口
        messagebox.showinfo("设置", "配置已保存。")  # 弹出信息提示框
        settings_window.destroy()  # 关闭设置窗口
        self.restart_app()  # 重启应用程序
    else:
        # 如果用户选择取消，不保存更改，并关闭设置窗口
        settings_window.destroy()
        return  # 返回

def on_settings_close(self, settings_window):  # 设置窗口关闭
    settings_window.destroy()  # 关闭设置窗口
    self.master.deiconify()  # 重新显示主窗口

def center_window_on_parent(self, child, width, height):
    """将子窗口置于父窗口中央"""
    # 获取父窗口的位置和大小
    parent_x = self.master.winfo_x()  # 获取父窗口的x坐标
    parent_y = self.master.winfo_y()  # 获取父窗口的y坐标
    parent_width = self.master.winfo_width()  # 获取父窗口的宽度
    parent_height = self.master.winfo_height()  # 获取父窗口的高度
    # 计算子窗口在父窗口中央的位置
    x = parent_x + (parent_width - width) // 2  # 计算子窗口的x坐标
    y = parent_y + (parent_height - height) // 2  # 计算子窗口的y坐标
    # 设置子窗口的位置和大小
    child.geometry(f"{width}x{height}+{x}+{y}")  # 设置子窗口的宽度、高度、和位置

def on_destroy(self, hwnd, msg, wparam, lparam):
    """处理窗口销毁消息"""
    self.settings_manager.save_config_to_disk()  # 保存配置到磁盘