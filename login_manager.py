import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
import base64
import json
import os
import webbrowser  # 导入webbrowser，用于在浏览器中打开URL
import socket
import urllib
from pystray import MenuItem as item
import pystray
from PIL import Image
import logging

class CampusNetLogin:  
    def __init__(self, master, settings_manager, show_ui=True):  # 初始化方法
        self.master = master  # 初始化主窗口
        self.config_lock = threading.Lock()  # 初始化线程锁用于保护配置文件的读写
        self.settings_manager = settings_manager  # 初始化设置管理器
        self.config = self.settings_manager.load_or_create_config()  # 加载配置文件
        self.key, self.cipher_suite = self.load_or_generate_key()  # 获取加密密钥

        self.eye_open_icon = tk.PhotoImage(
            file="./icons/eye_open.png"
        )  # 导入眼睛图标-打开状态
        self.eye_closed_icon = tk.PhotoImage(
            file="./icons/eye_closed.png"
        )  # 导入眼睛图标-关闭状态
        self.password_visible = False  # 跟踪密码是否可见的标志

        # 初始化ISP下拉列表的变量，并使用配置文件中的ISP设置，如果没有则默认为"campus"
        self.isp_var = tk.StringVar(value=self.config.get("isp", "campus"))

        self.show_ui = show_ui  # 是否显示UI界面的标志
        if show_ui:
            self.setup_ui()  # 初始化UI界面
        self.auto_login()  # 执行自动登录操作
    
    def load_config(self):  # 加载配置
        # 定义加载配置的函数，使用load_or_create_config函数来加载配置
        return self.settings_manager.load_or_create_config()

    def get_ip():
        # 获取本机IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建套接字对象
        try:
            s.connect(("8.8.8.8", 80))  # 连接到谷歌DNS服务器，获取本机IP地址
            ip = s.getsockname()[0]  # 获取本机IP地址
        finally:
            s.close()  # 关闭套接字连接
        return ip  # 返回本机IP地址

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

    def login(self):  # 登录
        # 从输入框获取用户名和密码
        username = self.username_entry.get()  # 从用户名输入框获取用户名
        password = self.password_entry.get()  # 从密码输入框获取密码
        if self.validate_credentials(
            username, password
        ):  # 调用验证函数检查用户名和密码是否为空
            # 启动后台线程执行登录操作，并传递用户名和密码
            login_thread = threading.Thread(
                target=self.perform_login, args=(username, password, False)
            )
            login_thread.start()  # 启动登录线程
        else:  # 如果用户名或密码为空
            messagebox.showwarning(
                "验证失败", "用户名或密码为空，请按要求填写。"
            )  # 显示警告框，提示用户名或密码为空

    def validate_credentials(username, password):
        """验证用户名和密码是否为空"""
        if not username or not password:  # 如果用户名或密码为空
            logging.warning("验证失败：用户名或密码为空")
            # 记录警告信息：用户名或密码为空
            return False  # 返回False
        return True  # 返回True

    def decode_base64_message(b64message):
        """解码Base64消息"""
        try:
            return base64.b64decode(b64message).decode(
                "utf-8"
            )  # 尝试解码Base64消息并以utf-8编码返回
        except Exception as e:  # 处理Base64消息解码异常
            logging.error(
                f"Base64消息解码失败:{e}"
            )  # 记录错误日志，提示Base64消息解码失败
            return None

    def load_login_responses():
        # 加载登录响应配置
        config_file_path = "./login_responses.json"  # 配置文件路径
        try:
            with open(
                config_file_path, "r", encoding="utf-8"
            ) as file:  # 以只读模式打开配置文件
                login_responses = json.load(file)  # 从文件中加载JSON数据
            return login_responses  # 返回加载的JSON数据
        except IOError as e:
            # 文件打开失败的处理代码
            print(f"Error opening the configuration file: {e}")  # 打印错误信息
        except json.JSONDecodeError as e:
            # JSON解码失败的处理代码
            print(f"Error parsing the configuration file: {e}")  # 打印错误信息

    # 处理登录结果
    def handle_login_result(self, response_dict, username, password, remember):
        # 从JSON文件加载响应配置
        response_config = self.load_login_responses()

        result = response_dict.get("result")  # 获取响应中的结果
        ret_code = response_dict.get("ret_code")  # 获取响应中的返回码
        msg = response_dict.get("msg")  # 获取响应中的消息

        # 根据结果和返回码确定结果
        outcome = ""  # 初始化结果
        if result == "1":  # 如果结果为"1"，表示成功
            outcome = "success"  # 结果为成功
        elif result == "0" and ret_code == 2:  # 如果结果为"0"且返回码为2,表示已经登录
            outcome = "already_logged_in"  # 结果为已经登录
        elif result == "0" and ret_code == 1:  # 如果结果为"0"且返回码为1,表示登录失败
            decode_msg = self.decode_base64_message(msg)  # 解码消息
            outcome = decode_msg  # 结果为解码后的消息
        else:
            # 未知登录错误
            logging.error(f"未知登录错误：{response_dict}")
            # 打开网页提示用户重新登录
            self.master.after(0, lambda: webbrowser.open("http://172.21.255.105/"))
            # 尝试打开常见问题文档
            self.master.after(
                0, lambda: os.startfile(os.path.join(os.getcwd(), "FAQ.docx"))
            )
            self.master.after(
                0,
                lambda: self.show_notification(
                    "登录失败",
                    "未知登录错误，请去报告错误界面提交错误提示后重新尝试",
                    self.config["icons"]["unknown"],
                ),
            )  # 显示通知
            return  # 返回

        response = response_config.get(outcome)  # 根据结果获取相应的响应配置

        if response:  # 如果存在响应配置
            # 执行相应的操作
            message1 = response["message1"]  # 获取通知
            message2 = response["message2"]  # 获取解决方案
            icon = response["icon"]  # 获取图标
            action = response["action"]  # 获取操作
        else:
            # 获取未知的登录失败的响应配置
            message1 = "未知错误"  # 获取通知
            message2 = (
                "未知错误，请去报告错误界面提交错误提示后重新尝试"  # 获取解决方案
            )
            icon = "unknown"  # 获取图标
            action = "unknown error"  # 获取操作

        self.execute_response_action(
            outcome, message1, message2, icon, action, username, password, remember
        )  # 执行响应的操作

    # 根据响应配置执行相应操作
    def execute_response_action(
        self, outcome, message1, message2, icon, action, username, password, remember
    ):
        self.show_notification(
            message1, "校园网状态", self.config["icons"][icon]
        )  # 显示通知
        if action == "already_logged_in" or action == "success":  # 用户已经登录的处理
            if remember:  # 如果记住密码
                # 保存凭据
                self.master.after(
                    0, lambda: self.save_credentials(username, password, remember)
                )
            if action == "already_logged_in":  # 如果操作为用户已经登录
                logging.info(f"用户 {username} 已经登录")  # 记录信息：用户已经登录
            elif action == "success":  # 如果操作为登录成功
                logging.info(f"用户 {username} 登录成功")  # 记录信息：用户登录成功
                # 根据配置决定是最小化到托盘还是退出程序
                if self.config.get("minimize_to_tray_on_login", True):
                    self.master.after(
                        0, self.hide_window
                    )  # 如果配置为 True 则最小化到托盘
                else:
                    self.master.after(0, self.quit_app)  # 如果配置为 False 则退出程序
        else:  # 处理各种失败情况
            self.show_error_message("登录失败", message2)  # 显示错误消息
            if action == "show_web1":  # 如果操作为打开网页1
                self.master.after(
                    0, lambda: webbrowser.open("http://172.30.1.100:8080/Self/login/")
                )  # 打开网页1
            elif action == "clear_credentials1":  # 如果操作为处理密码错误情况
                logging.warning(
                    f"用户 {username} 密码错误，尝试的错误密码为：{password}"
                )  # 记录警告：用户密码错误
                self.clear_saved_credentials()  # 清除保存的凭据
            elif action == "clear_credentials2":  # 如果操作为处理账号或运营商错误情况
                logging.warning(
                    f"账号或运营商错误，尝试的错误账号为：{username}，错误运营商为：{self.isp_var.get()}"
                )  # 记录警告：账号或运营商错误
                self.clear_saved_credentials()  # 清除保存的凭据
            elif action == "show_web2":  # 如果操作为打开网页2
                self.master.after(
                    0, lambda: webbrowser.open("http://172.21.255.105/")
                )  # 打开网页2
            else:  # 处理未知错误情况
                logging.warning(f"未知错误：{outcome}")
                # 打开网页提示用户重新登录
                self.master.after(0, lambda: webbrowser.open("http://172.21.255.105/"))
                # 尝试打开常见问题文档
                self.master.after(
                    0, lambda: os.startfile(os.path.join(os.getcwd(), "FAQ.docx"))
                )

    # 加载登录响应配置
    def perform_login(self, username, password, auto=False):
        logging.debug(
            f"开始登录流程，用户名: {username}, 自动登录: {str(auto)}"
        )  # 记录调试信息
        # 运营商标识映射
        isp_codes = {
            "中国电信": "@telecom",  # 中国电信
            "中国移动": "@cmcc",  # 中国移动
            "中国联通": "@unicom",  # 中国联通
            "校园网": "@campus",  # 校园网
        }
        selected_isp_code = isp_codes.get(self.isp_var.get(), "@campus")  # 默认为校园网

        logging.info(
            f"尝试登录：用户名 {username}，运营商：{self.isp_var.get()}，密码已提交"
        )  # 记录信息：尝试登录
        remember = self.remember_var.get() == 1 if not auto else True  # 记住密码

        # URL编码用户名和密码
        encoded_username = urllib.parse.quote(username)
        encoded_password = urllib.parse.quote(password)

        # 拼接完整的登录参数
        sign_parameter = f"{self.config['api_url']}?c=Portal&a=login&callback=dr1004&login_method=1&user_account={encoded_username}{selected_isp_code}&user_password={encoded_password}&wlan_user_ip={self.get_ip()}"

        try:
            # 发送登录请求并将响应存储在名为'response'的变量中
            response = requests.get(sign_parameter, timeout=5).text
            logging.info(
                f"登录请求发送成功，响应: {response}"
            )  # 记录信息：登录请求发送成功
            response_dict = json.loads(
                response[response.find("{") : response.rfind("}") + 1]
            )  # 解析响应为字典形式

            self.handle_login_result(
                response_dict, username, password, remember
            )  # 处理登录结果的函数调用

        except Exception as e:  # 处理登录请求异常
            # 记录登录过程中的异常信息
            logging.error(f"登录过程中发生异常：{e}", exc_info=True)
            self.master.after(
                0,
                lambda: self.show_notification(
                    "登录过程中发生异常",
                    "发生未知网络错误。",
                    self.config["icons"]["unknown"],
                ),
            )  # 显示通知

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