
# 用户凭据管理类
class CredentialsManager:
    def save_credentials(self, username, password, remember):
        # 保存用户凭据信息
        if password is None:
            logging.error(
                "尝试保存的密码为None。"
            )  # 记录错误信息：尝试保存的密码为None
            return  # 直接返回，避免进一步处理None类型的密码

        encrypted_password = self.cipher_suite.encrypt(password.encode())  # 加密密码
        # 组装凭据信息，包括运营商
        credentials = {
            "username": username,  # 用户名
            "password": encrypted_password,  # 加密后的密码
            "isp": self.isp_var.get(),  # 运营商
            "remember": remember,  # 是否记住密码
        }
        with open(
            "encrypted_credentials.pkl", "wb"
        ) as file:  # 以二进制写入模式打开文件
            pickle.dump(credentials, file)  # 将凭据信息序列化保存到文件中

        logging.info(
            f"保存凭据：用户名 {username}, 记住密码：{'是' if remember else '否'}, 运营商：{self.isp_var.get()}"
        )  # 记录保存凭据的信息

        # 保存运营商选择
        isp_reverse_mapping = {
            "中国电信": "telecom",  # 中国电信
            "中国移动": "cmcc",  # 中国移动
            "中国联通": "unicom",  # 中国联通
            "campus": "校园网",  # 校园网
        }  # 定义运营商映射关系
        self.config["isp"] = isp_reverse_mapping.get(
            self.isp_var.get(), "campus"
        )  # 获取用户选择的运营商映射值，默认为校园网
        self.settings_manager.save_config(self.config)  # 保存配置信息

    def load_credentials(self):  # 加载凭据
        try:
            # 尝试打开名为'encrypted_credentials.pkl'的文件
            with open(
                "encrypted_credentials.pkl", "rb"
            ) as file:  # 以二进制读取模式打开文件
                # 从文件中加载凭据
                credentials = pickle.load(file)
                # 获取用户名和解密后的密码
                username = credentials["username"]
                password = self.cipher_suite.decrypt(credentials["password"]).decode()
                isp = credentials.get("isp", "campus")  # 默认运营商为校园网
                remember = credentials.get("remember", False)  # 默认不记住密码
                return (
                    username,
                    password,
                    isp,
                    remember,
                )  # 返回用户名、密码、运营商和是否记住密码
        except FileNotFoundError:  # 处理文件未找到异常
            # 若文件未找到，则返回空值
            return "", "", "campus", False

    def clear_saved_credentials():  # 清除保存的凭据
        try:
            # 尝试删除名为'encrypted_credentials.pkl'的文件
            os.remove("encrypted_credentials.pkl")
        except FileNotFoundError:
            # 若文件未找到，则忽略异常
            pass

    def clear_key_and_credentials(self):
        """清除存储的加密密钥，如果找到，则清除用户凭证"""
        confirm = messagebox.askyesno(
            "确认清除", "这将清除所有保存的用户凭证和加密密钥。您确定要继续吗?"
        )  # 弹出确认对话框，让用户确认清除操作
        if confirm:  # 如果用户选择确认
            key_cleared = False  # 初始化加密密钥清除标志为False
            credentials_cleared = False  # 初始化用户凭证清除标志为False

            # 尝试删除密钥文件
            try:
                os.remove("encryption_key.key")  # 删除密钥文件
                logging.info("加密密钥已被清除。")  # 记录日志，说明加密密钥已被清除
                key_cleared = True  # 设置加密密钥清除标志为True
            except FileNotFoundError:  # 如果找不到密钥文件
                logging.warning(
                    "找不到密钥文件，无法删除。"
                )  # 记录警告日志，说明找不到密钥文件

            # 尝试删除凭证文件
            try:
                os.remove("encrypted_credentials.pkl")  # 删除凭证文件
                logging.info("用户凭证已被清除。")  # 记录日志，说明用户凭证已被清除
                credentials_cleared = True  # 设置用户凭证清除标志为True
            except FileNotFoundError:  # 如果找不到凭证文件
                logging.warning(
                    "找不到凭证文件，无法删除。"
                )  # 记录警告日志，说明找不到凭证文件

            # 根据文件清除的情况给出相应的提示
            if key_cleared and credentials_cleared:  # 如果加密密钥和用户凭证均已被清除
                messagebox.showinfo(
                    "清除完成", "加密密钥和用户凭证均已被清除。"
                )  # 弹出信息提示框
            elif key_cleared:  # 如果仅清除了加密密钥
                messagebox.showinfo(
                    "清除完成", "加密密钥已被清除，未找到用户凭证。"
                )  # 弹出信息提示框
            elif credentials_cleared:  # 如果仅清除了用户凭证
                messagebox.showinfo(
                    "清除完成", "用户凭证已被清除，未找到加密密钥。"
                )  # 弹出信息提示框
            else:  # 如果加密密钥和用户凭证均未被清除
                messagebox.showinfo(
                    "清除失败", "未找到加密密钥和用户凭证，无需进行清除。"
                )  # 弹出信息提示框

            # 如果至少清除了一个文件，则重启应用
            if key_cleared or credentials_cleared:
                self.restart_app()  # 重启应用程序

    def clear_credentials(self):
        """仅清除存储的用户凭证"""
        # 弹出确认对话框，让用户确认清除操作
        confirm = messagebox.askyesno(
            "确认清除", "这将清除所有保存的用户凭证。您确定要继续吗？"
        )
        if confirm:  # 如果用户选择确认
            try:
                # 尝试删除存储用户凭证的文件
                os.remove("encrypted_credentials.pkl")  # 删除用户凭证文件
                logging.info("用户凭证已被清除。")  # 记录日志，说明用户凭证已被清除
                # 弹出信息提示框，告知用户凭证已被清除
                messagebox.showinfo("清除完成", "所有保存的用户凭证已被清除。")
                self.restart_app()  # 重新启动应用程序
            except FileNotFoundError:  # 如果找不到凭证文件
                logging.warning(
                    "找不到凭证文件，无法删除。"
                )  # 记录警告日志，说明找不到凭证文件
                # 弹出信息提示框，告知用户未找到用户凭证文件，无需清除
                messagebox.showinfo("清除失败", "没有找到用户凭证文件，无需进行清除。")