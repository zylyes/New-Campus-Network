
# 通知管理类
class NoticeManager:
    def show_notification(self, title, msg, icon_path=None):
        """显示通知的方法"""
        wc = win32gui.WNDCLASS()  # 创建WNDCLASS实例
        wc.hInstance = win32api.GetModuleHandle(None)  # 获取当前实例句柄
        wc.lpszClassName = "CampusNetLoginAppNotification"  # 设置窗口类名
        wc.lpfnWndProc = {
            win32con.WM_DESTROY: self.on_destroy
        }  # 设置窗口消息处理函数，处理销毁消息

        try:
            class_atom = win32gui.RegisterClass(wc)  # 注册窗口类
        except pywintypes.error as e:  # 捕获Windows API错误
            if "类已存在。" in str(e):
                # 类已存在，可以继续使用
                pass  # 什么也不做
            else:
                raise  # 重新抛出其他类型的异常

        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU  # 设置窗口样式
        self.hwnd = win32gui.CreateWindow(
            "CampusNetLoginAppNotification",
            "CampusNetLoginApp Notification Window",
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            wc.hInstance,
            None,
        )  # 创建窗口
        win32gui.UpdateWindow(self.hwnd)  # 更新窗口

        # 显示通知。
        if icon_path and os.path.isfile(
            icon_path
        ):  # 检查是否有指定图标路径并且文件存在
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(
                None, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags
            )  # 加载图标
        else:  # 如果没有指定图标路径或文件不存在
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)  # 使用默认图标

        flags = (
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        )  # 设置通知图标的标志
        nid = (
            self.hwnd,
            0,
            flags,
            win32con.WM_USER + 20,
            hicon,
            "Tooltip",
        )  # 设置通知图标的属性
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)  # 添加通知图标
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (
                self.hwnd,
                0,
                win32gui.NIF_INFO,
                win32con.WM_USER + 20,
                hicon,
                "Balloon Tooltip",
                msg,
                200,
                title,
            ),
        )  # 修改通知为气球提示
        timer = threading.Timer(5.0, self.clear_notification_icon)  # 5秒后执行清理
        timer.start()  # 启动定时器

    def clear_notification_icon(self):
        """清理通知图标的方法"""
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))  # 删除通知图标

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """处理窗口销毁消息"""
        self.settings_manager.save_config_to_disk()  # 保存配置到磁盘