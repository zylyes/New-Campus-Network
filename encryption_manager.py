# 加密管理器

import os  # 导入os库，用于处理操作系统级别的接口，如文件管理
from cryptography.fernet import Fernet  # 从cryptography库导入Fernet，用于加密
import logging  # 导入logging库，用于记录日志
from tkinter import messagebox # 从tkinter导入messagebox和ttk，用于图形界面中的对话框和高级组件

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