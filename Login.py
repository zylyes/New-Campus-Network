import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
import os
import json
import socket
import urllib
from pystray import MenuItem as item
from cryptography.fernet import Fernet
import pystray
from PIL import Image
import logging

class CampusNetLogin:  
    def __init__(self, master, settings_manager, show_ui=True):  
        self.master = master  
        self.settings_manager = settings_manager  
        self.config = self.settings_manager.load_or_create_config()  
        self.key, self.cipher_suite = self.load_or_generate_key()  

        self.eye_open_icon = tk.PhotoImage(file="./icons/eye_open.png")  
        self.eye_closed_icon = tk.PhotoImage(file="./icons/eye_closed.png")  
        self.password_visible = False  

        self.isp_var = tk.StringVar(value=self.config.get("isp", "campus"))  
        self.show_ui = show_ui  
        if show_ui:
            self.setup_ui()  
        self.auto_login()  

    def auto_login(self):
        """自动登录逻辑"""
        if self.config.get("remember_credentials", False):
            username = self.config.get("username", "")
            password = self.decrypt_password(self.config.get("password", ""))
            if username and password:
                self.username_entry.insert(0, username)
                self.password_entry.insert(0, password)
                self.remember_var.set(1)
                # 执行自动登录
                self.perform_login(username, password, auto=True)

    @staticmethod  
    def load_or_generate_key():  
        key_file = "encryption_key.key"  
        if os.path.exists(key_file):  
            with open(key_file, "rb") as file:  
                key = file.read()  
        else:  
            key = Fernet.generate_key()  
            with open(key_file, "wb") as file:  
                file.write(key)  
        return key, Fernet(key)  

    @staticmethod  
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        try:
            s.connect(("8.8.8.8", 80))  
            ip = s.getsockname()[0]  
        finally:
            s.close()  
        return ip  

    def login(self):  
        username = self.username_entry.get()  
        password = self.password_entry.get()  
        if self.validate_credentials(username, password):  
            login_thread = threading.Thread(target=self.perform_login, args=(username, password, False))
            login_thread.start()  
        else:  
            messagebox.showwarning("验证失败", "用户名或密码为空，请按要求填写。")  

    def perform_login(self, username, password, auto=False):
        isp_codes = {
            "中国电信": "@telecom",  
            "中国移动": "@cmcc",  
            "中国联通": "@unicom",  
            "校园网": "@campus",  
        }
        selected_isp_code = isp_codes.get(self.isp_var.get(), "@campus")  

        encoded_username = urllib.parse.quote(username)
        encoded_password = urllib.parse.quote(password)

        sign_parameter = f"{self.config['api_url']}?c=Portal&a=login&callback=dr1004&login_method=1&user_account={encoded_username}{selected_isp_code}&user_password={encoded_password}&wlan_user_ip={self.get_ip()}"

        try:
            response = requests.get(sign_parameter, timeout=5).text
            response_dict = json.loads(response[response.find("{") : response.rfind("}") + 1])
            self.handle_login_result(response_dict, username, password, remember=True if auto else False)  
        except Exception as e:  
            logging.error(f"登录过程中发生异常：{e}", exc_info=True)

    def setup_ui(self):  
        self.master.title("校园网自动登录")  
        main_frame = ttk.Frame(self.master)  
        main_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)  

        ttk.Label(main_frame, text="用户名：", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="ew")  
        self.username_entry = ttk.Entry(main_frame)  
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  

        ttk.Label(main_frame, text="密码：", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="ew")  
        self.password_entry = ttk.Entry(main_frame, show="*")  
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")  

        self.toggle_password_btn = tk.Button(
            main_frame,
            image=self.eye_closed_icon,
            command=self.toggle_password_visibility,
            borderwidth=0,
        )  
        self.toggle_password_btn.grid(row=1, column=2, padx=5, pady=5, sticky="w")  

        self.remember_var = tk.IntVar()  
        ttk.Checkbutton(main_frame, text="记住账号和密码", variable=self.remember_var).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w")  

        ttk.Button(main_frame, text="登录", command=self.login).grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")  

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.config(show="*")
            self.toggle_password_btn.config(image=self.eye_closed_icon)
            self.password_visible = False
        else:
            self.password_entry.config(show="")
            self.toggle_password_btn.config(image=self.eye_open_icon)
            self.password_visible = True

    def hide_window(self):
        self.master.withdraw()  
        icon_image = Image.open("./icons/ECUT.ico")
        self.icon = pystray.Icon("campus_net_login", icon=icon_image, title="校园网自动登录", menu=pystray.Menu(
            item("打开", self.show_window, default=True),
            item("退出", lambda icon, item: self.quit_app(icon)),
        ))
        self.icon.run_detached()

    def quit_app(self, icon=None, item=None):  
        if icon:  
            icon.stop()  
        self.master.quit()  
        self.master.destroy()