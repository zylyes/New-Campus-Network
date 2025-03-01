import tkinter as tk
from tkinter import ttk
from app.utils.config import Config

class SettingsWindow:
    def __init__(self, root):
        self.root = root
        self.config = Config().load_config()
        self.setup_ui()

    def setup_ui(self):
        self.root.title("设置")
        self.api_url_entry = ttk.Entry(self.root)
        self.api_url_entry.insert(0, self.config.get("api_url"))
        self.save_button = ttk.Button(self.root, text="保存", command=self.save_settings)
        self.api_url_entry.grid(row=0, column=1)
        self.save_button.grid(row=1, column=1)

    def save_settings(self):
        api_url = self.api_url_entry.get()
        self.config["api_url"] = api_url
        Config().save_config(self.config)
        messagebox.showinfo("设置", "配置已保存")