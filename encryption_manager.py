from tkinter import (
    messagebox,
)  # 从tkinter导入messagebox，用于图形界面中的对话框和高级组件
import os  # 导入os库，用于处理操作系统级别的接口，如文件管理
from cryptography.fernet import Fernet  # 从cryptography库导入Fernet，用于加密
import logging  # 导入logging库，用于记录日志
import pickle  # 导入pickle库，用于对象的序列化和反序列化

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