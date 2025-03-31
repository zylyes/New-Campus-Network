# 托盘管理器
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image

def show_window(self, icon=None, item=None):
        """从托盘恢复窗口"""
        if icon:  # 如果提供了icon参数
            icon.stop()  # 停止托盘图标
        self.master.deiconify()  # 显示窗口
        self.setup_ui()  # 重新设置或刷新UI界面

def hide_window(self):
    """隐藏窗口并显示托盘图标"""
    self.master.withdraw()  # 隐藏窗口

    def setup_system_tray():  # 设置系统托盘
        # 加载托盘图标
        icon_image = Image.open("./icons/ECUT.ico")

        # 创建托盘图标
        self.icon = pystray.Icon(
            "campus_net_login",  # 托盘图标的名称
            icon=icon_image,  # 托盘图标的图像
            title="校园网自动登录",  # 托盘图标的标题
            menu=pystray.Menu(
                item("打开", self.show_window, default=True),
                item("退出", lambda icon, item: self.quit_app(icon)),
            ),  # 托盘图标的菜单
        )
        # 运行托盘图标
        self.icon.run_detached()

    # 在后台线程中设置系统托盘，防止阻塞主线程
    threading.Thread(target=setup_system_tray).start()

def quit_app(self, icon=None, item=None):  # 退出应用
    if icon:  # 如果提供了icon参数
        icon.stop()  # 停止托盘图标
    # 保存配置，清理资源，退出程序的其余步骤
    self.master.quit()
    # 可能有必要的清理步骤
    self.master.destroy()