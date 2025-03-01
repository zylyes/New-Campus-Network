import pystray
from PIL import Image
import logging

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self._create_icon()

    def _create_icon(self):
        try:
            menu = pystray.Menu(
                pystray.MenuItem("打开主界面", self.app.show_window),
                pystray.MenuItem("退出", self.app.quit_app)
            )
            image = Image.open("icons/tray_icon.png")
            self.icon = pystray.Icon("campus_net", image, "校园网登录", menu)
        except Exception as e:
            logging.error(f"Tray icon creation failed: {str(e)}")

    def run(self):
        if self.icon:
            self.icon.run_detached()