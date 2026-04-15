"""
主窗口应用
Tkinter GUI主应用，管理页面切换
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import tkinter as tk
from tkinter import ttk
from core.config_manager import ConfigManager


class AliveCheckApp:
    """政务局黑名单信息对比客户端主应用"""

    def __init__(self):
        """初始化应用"""
        self.root = tk.Tk()
        self.root.title("政务局黑名单信息对比客户端")
        self.root.geometry("550x600")
        self.root.resizable(True, True)

        # 设置最小窗口大小
        self.root.minsize(500, 500)

        # 加载配置管理器
        self.config_manager = ConfigManager()

        # 当前配置
        self.current_config = None

        # 创建主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # 当前显示的面板
        self.current_panel = None

        # 显示配置面板
        self.show_config_panel()

    def show_config_panel(self):
        """显示配置面板"""
        self.clear_panel()

        from gui.config_panel import ConfigPanel
        self.current_panel = ConfigPanel(
            self.main_frame,
            self.config_manager,
            self.on_config_next
        )
        self.current_panel.pack(fill='both', expand=True)

    def show_process_panel(self):
        """显示处理面板"""
        self.clear_panel()

        from gui.process_panel import ProcessPanel
        self.current_panel = ProcessPanel(
            self.main_frame,
            self.current_config,
            self.on_process_back,
            self.on_process_complete
        )
        self.current_panel.pack(fill='both', expand=True)

    def clear_panel(self):
        """清除当前面板"""
        if self.current_panel:
            self.current_panel.destroy()
            self.current_panel = None

    def on_config_next(self, config):
        """配置完成，进入处理"""
        self.current_config = config
        self.show_process_panel()

    def on_process_back(self):
        """返回配置"""
        self.show_config_panel()

    def on_process_complete(self, result):
        """处理完成，显示结果"""
        from gui.result_dialog import ResultDialog
        ResultDialog(self.root, result)

    def run(self):
        """运行应用"""
        # 居中窗口
        self.center_window()
        self.root.mainloop()

    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
