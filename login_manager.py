# 登录管理器
import tkinter as tk  # 导入tkinter库，用于GUI界面创建
from tkinter import messagebox # 从tkinter导入messagebox和ttk，用于图形界面中的对话框和高级组件
import requests  # 导入requests库，用于处理HTTP请求
import os  # 导入os库，用于处理操作系统级别的接口，如文件管理
import json  # 导入json库，用于处理JSON数据格式
import logging  # 导入logging库，用于记录日志
import socket  # 导入socket库，用于网络通信
import threading  # 导入threading库，用于多线程编程
import time  # 导入time库，用于时间操作
import base64  # 导入base64库，用于编码和解码base64数据
import webbrowser  # 导入webbrowser，用于在浏览器中打开URL
import urllib.parse  # 导入urllib库，用于URL编码
from ui_manager import setup_ui, center_window_on_parent, on_settings_close, save_settings_and_close  # 导入setup_ui函数、center_window_on_parent、on_settings_close和save_settings_and_close
from encryption_manager import load_or_generate_key, clear_key_and_credentials, clear_credentials # 导入自定义函数，用于加载或生成密钥以及清除密钥和凭据
from config_manager import load_credentials  # 导入加载凭据的函数
from mutex_manager import apply_auto_start_setting, restart_app  # 导入 apply_auto_start_setting 和 restart_app 方法

class CampusNetLogin:  
    def __init__(self, master, settings_manager, show_ui=True):  # 初始化方法
        self.master = master  # 初始化主窗口
        self.config_lock = threading.Lock()  # 初始化线程锁用于保护配置文件的读写
        self.settings_manager = settings_manager  # 初始化设置管理器
        self.config = self.settings_manager.load_or_create_config()  # 加载配置文件
        self.key, self.cipher_suite = load_or_generate_key()  # 获取加密密钥

        self.eye_open_icon = tk.PhotoImage(
            file="./icons/eye_open.png"
        )  # 导入眼睛图标-打开状态
        self.eye_closed_icon = tk.PhotoImage(
            file="./icons/eye_closed.png"
        )  # 导入眼睛图标-关闭状态
        self.password_visible = False  # 跟踪密码是否可见的标志

        # 初始化ISP下拉列表的变量，并使用配置文件中的ISP设置，如果没有则默认为"campus"
        self.isp_var = tk.StringVar(value=self.config.get("isp", "campus"))

        self.minimize_to_tray_var = tk.IntVar(value=self.config.get("minimize_to_tray_on_login", True))
        self.auto_start_var = tk.IntVar(value=self.config.get("auto_start", False))
        self.auto_login_var = tk.IntVar(value=self.config.get("auto_login", False))

        self.show_ui = show_ui  # 是否显示UI界面的标志
        self.setup_ui = lambda: setup_ui(self)  # 将setup_ui函数绑定到实例方法
        self.center_window_on_parent = lambda child, width, height: center_window_on_parent(self, child, width, height)  # 绑定center_window_on_parent
        self.on_settings_close = lambda settings_window: on_settings_close(self, settings_window)  # 绑定 on_settings_close 方法
        self.save_settings_and_close = lambda api_url, settings_window, config, minimize_to_tray_var, auto_start_var, auto_login_var: save_settings_and_close(
            self, api_url, settings_window
        )  # 绑定 save_settings_and_close 方法
        self.restart_app = lambda: restart_app(self)  # 绑定 restart_app 方法
        if show_ui:
            self.setup_ui()  # 调用setup_ui函数
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

    def auto_login(self):  # 自动登录
        if self.config.get("auto_login", False):  # 检查配置是否要求自动登录
            username, password, isp, remember = load_credentials(self.config)  # 调用加载凭据函数
            if username and password:  # 如果用户名和密码存在
                self.isp_var.set(isp)  # 设置运营商变量
                # 使用加载的凭据进行登录
                self.perform_login(username, password, auto=True)
            else:
                # 如果没有有效的凭据，显示UI以便用户可以手动输入
                if self.show_ui:  # 如果配置中启用了自动登录
                    self.setup_ui()  # 显示UI
        else:
            # 如果配置中未启用自动登录，则总是显示UI
            self.setup_ui()

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
        sign_parameter = (
            f"{self.config['api_url']}?user_account={encoded_username}{selected_isp_code}"
            f"&user_password={encoded_password}&ac_id=1&action=login"
        )  # 定义登录请求的完整URL

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

    def show_error_message(title, message):
        """显示错误信息和用户指导"""
        messagebox.showerror(title, message)  # 弹出错误信息对话框，显示标题和消息

    def save_error_report(report):  # 保存错误报告
        filename = "error_reports.txt"  # 错误报告保存到的文件名
        with open(filename, "a") as file:  # 以追加模式打开文件
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()
            )  # 获取当前时间戳
            file.write(f"{timestamp}: {report}\n\n")  # 将错误报告和时间戳写入文件

    def report_error(self):
        # 创建一个新的顶级窗口用于报告错误
        error_report_window = tk.Toplevel(self.master)  # 创建一个新的顶级窗口
        error_report_window.title("报告错误")  # 设置窗口标题为"报告错误"

        # 添加标签提示用户描述问题或提供反馈
        tk.Label(error_report_window, text="请描述遇到的问题或提供反馈：").pack(
            padx=10, pady=5
        )
        error_text = tk.Text(error_report_window, height=10, width=50)  # 创建文本框
        error_text.pack(padx=10, pady=5)  # 将文本框放置在窗口中

        def submit_report():  # 提交错误报告
            # 获取用户输入的错误描述并去除首尾空格
            report_content = error_text.get("1.0", "end").strip()
            if report_content:  # 如果错误描述不为空
                # 调用save_error_report方法保存错误报告
                self.save_error_report(report_content)
                messagebox.showinfo(
                    "报告错误", "您的反馈已提交，谢谢！"
                )  # 弹出信息提示框
                error_report_window.destroy()  # 销毁报告错误窗口
            else:  # 如果错误描述为空
                messagebox.showwarning(
                    "报告错误", "错误描述不能为空。"
                )  # 弹出警告提示框

        # 添加提交按钮，点击提交按钮时执行submit_report函数
        tk.Button(error_report_window, text="提交", command=submit_report).pack(pady=5)

    def open_suggestion_box(self):  # 打开建议框
        suggestion_window = tk.Toplevel(self.master)  # 创建一个新的顶级窗口用于提交建议
        suggestion_window.title("提交建议")  # 设置窗口标题为"提交建议"

        tk.Label(suggestion_window, text="请分享您的建议或反馈：").pack(
            padx=10, pady=5
        )  # 在窗口中添加文本标签
        suggestion_text = tk.Text(
            suggestion_window, height=10, width=50
        )  # 创建一个文本框用于输入建议
        suggestion_text.pack(padx=10, pady=5)  # 将文本框放置在窗口中

        def submit_suggestion():  # 提交建议
            suggestion_content = suggestion_text.get(
                "1.0", "end"
            ).strip()  # 获取用户输入的建议并去除首尾空格
            if suggestion_content:  # 如果建议内容不为空
                self.save_suggestion(
                    suggestion_content
                )  # 调用save_suggestion方法保存建议
                messagebox.showinfo(
                    "提交建议", "您的建议已提交，感谢您的反馈！"
                )  # 弹出信息提示框，确认建议已提交
                suggestion_window.destroy()  # 销毁提交建议窗口
            else:  # 如果建议内容为空
                messagebox.showwarning(
                    "提交建议", "建议内容不能为空。"
                )  # 弹出警告提示框，提醒建议内容不能为空

        tk.Button(suggestion_window, text="提交", command=submit_suggestion).pack(
            pady=5
        )  # 在窗口中添加提交按钮，并设置点击事件为submit_suggestion函数

    def save_suggestion(suggestion):  # 保存建议
        filename = "suggestions.txt"  # 建议保存到的文件名
        with open(filename, "a") as file:  # 打开文件并追加内容
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()
            )  # 获取当前时间戳
            file.write(f"{timestamp}: {suggestion}\n\n")  # 将建议和时间戳写入文件
        logging.info("用户建议已保存。")  # 记录日志信息

    def clear_key_and_credentials(self):
        """清除加密密钥和用户凭据"""
        clear_key_and_credentials(self)

    def clear_credentials(self):
        """仅清除用户凭据"""
        clear_credentials(self)

    def apply_auto_start_setting(self):
        """应用自动启动设置"""
        apply_auto_start_setting(self)  # 调用 mutex_manager 中的 apply_auto_start_setting 方法