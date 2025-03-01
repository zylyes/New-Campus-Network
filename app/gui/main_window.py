import tkinter as tk
from tkinter import ttk, messagebox
from ..core import NetworkService, SecurityManager
from ..utils.config import ConfigManager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("校园网自动登录")
        self.config_manager = ConfigManager()
        self.security = SecurityManager()
        self._setup_ui()
        self._load_credentials()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 用户名输入
        ttk.Label(main_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW)

        # 密码输入
        ttk.Label(main_frame, text="密码:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.EW)

        # ISP选择
        ttk.Label(main_frame, text="运营商:").grid(row=2, column=0, sticky=tk.W)
        self.isp_combobox = ttk.Combobox(
            main_frame,
            values=["中国电信", "中国移动", "中国联通", "校园网"],
            state="readonly"
        )
        self.isp_combobox.grid(row=2, column=1, sticky=tk.EW)
        self.isp_combobox.current(3)

        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="登录", command=self.on_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="设置", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        # 布局配置
        main_frame.columnconfigure(1, weight=1)

    def _load_credentials(self):
        # 加载保存的凭证
        pass  # 需要根据存储实现

    def on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        isp = self.isp_combobox.get()

        if not username or not password:
            messagebox.showwarning("输入错误", "用户名和密码不能为空")
            return

        url = NetworkService.build_login_url(
            self.config_manager["api_url"],
            username,
            password,
            isp
        )
        response = NetworkService.send_login_request(url)
        self.handle_response(response)

    def handle_response(self, response):
        # 处理登录响应
        pass

    def open_settings(self):
        # 打开设置窗口
        pass

    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.destroy()