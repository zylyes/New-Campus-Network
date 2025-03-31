
# 网络操作类
class NetworkManager:
    def get_ip():
        # 获取本机IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建套接字对象
        try:
            s.connect(("8.8.8.8", 80))  # 连接到谷歌DNS服务器，获取本机IP地址
            ip = s.getsockname()[0]  # 获取本机IP地址
        finally:
            s.close()  # 关闭套接字连接
        return ip  # 返回本机IP地址
    
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