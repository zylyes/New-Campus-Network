
# 主应用类
class LoginApp:
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

    def load_or_generate_key():  # 加载或生成密钥
        # 定义加载或生成密钥的函数
        key_file = "encryption_key.key"  # 密钥文件名
        if os.path.exists(key_file):  # 如果密钥文件已存在
            with open(key_file, "rb") as file:  # 以二进制读取模式打开密钥文件
                key = file.read()  # 从文件中读取密钥
        else:  # 如果密钥文件不存在
            key = Fernet.generate_key()  # 生成新的密钥
            logging.debug("新建密钥文件")  # 记录调试信息：新建密钥文件
            with open(key_file, "wb") as file:  # 以二进制写入模式打开密钥文件
                file.write(key)  # 将新生成的密钥写入文件
            messagebox.showinfo(
                "密钥生成", "新的加密密钥已生成并保存。"
            )  # 弹出提示框显示密钥已生成
        return key, Fernet(key)  # 返回密钥及使用该密钥初始化的Fernet对象
    
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

    def auto_login(self):  # 自动登录
        if self.config.get("auto_login", False):  # 检查配置是否要求自动登录
            username, password, isp, remember = self.load_credentials()  # 加载凭据
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