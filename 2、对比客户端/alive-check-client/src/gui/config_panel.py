"""
配置面板
第一步：用户配置接口信息
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api_client import ApiClient


class ConfigPanel(ttk.Frame):
    """配置面板"""

    def __init__(self, parent, config_manager, on_next_callback):
        """
        初始化配置面板
        :param parent: 父容器
        :param config_manager: 配置管理器
        :param on_next_callback: 下一步回调函数
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.on_next_callback = on_next_callback

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self, text="请配置接口信息", font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)

        # 配置表单
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=40, pady=10, fill='x')

        # 应用ID
        ttk.Label(form_frame, text="应用ID:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=8)
        self.app_id_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.app_id_entry.grid(row=0, column=1, pady=8, padx=10)

        # 应用密钥
        ttk.Label(form_frame, text="应用密钥:", font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=8)
        self.app_secret_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.app_secret_entry.grid(row=1, column=1, pady=8, padx=10)

        # Token接口地址
        ttk.Label(form_frame, text="Token接口:", font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=8)
        self.token_url_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.token_url_entry.grid(row=2, column=1, pady=8, padx=10)

        # 比对接口地址
        ttk.Label(form_frame, text="比对接口:", font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=8)
        self.compare_url_entry = ttk.Entry(form_frame, width=40, font=('Arial', 12))
        self.compare_url_entry.grid(row=3, column=1, pady=8, padx=10)

        # 保存目录
        ttk.Label(form_frame, text="保存目录:", font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=8)
        self.save_dir_entry = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.save_dir_entry.grid(row=4, column=1, pady=8, padx=10, sticky='w')
        self.save_dir_btn = ttk.Button(form_frame, text="选择...", command=self.select_save_dir)
        self.save_dir_btn.grid(row=4, column=2, pady=8)

        # 保存配置复选框
        self.save_config_var = tk.BooleanVar(value=True)
        save_config_check = ttk.Checkbutton(self, text="保存配置以便下次使用", variable=self.save_config_var)
        save_config_check.pack(pady=15)

        # 按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        # 测试连接按钮
        self.test_btn = ttk.Button(button_frame, text="测试连接", command=self.test_connection, width=12)
        self.test_btn.pack(side='left', padx=10)

        # 下一步按钮
        self.next_btn = ttk.Button(button_frame, text="下一步", command=self.go_next, width=12)
        self.next_btn.pack(side='left', padx=10)

        # 状态提示
        self.status_label = ttk.Label(self, text="", font=('Arial', 10), foreground='gray')
        self.status_label.pack(pady=10)

    def load_config(self):
        """加载已保存的配置"""
        self.app_id_entry.insert(0, self.config_manager.get('appId'))
        self.app_secret_entry.insert(0, self.config_manager.get('appSecret'))
        self.token_url_entry.insert(0, self.config_manager.get('tokenUrl'))
        self.compare_url_entry.insert(0, self.config_manager.get('compareUrl'))
        self.save_dir_entry.insert(0, self.config_manager.get('saveDir'))

    def select_save_dir(self):
        """选择保存目录"""
        current_dir = self.save_dir_entry.get() or os.path.expanduser('~')
        selected_dir = filedialog.askdirectory(initialdir=current_dir, title="选择保存目录")
        if selected_dir:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, selected_dir)

    def get_config(self):
        """获取当前配置"""
        return {
            'appId': self.app_id_entry.get().strip(),
            'appSecret': self.app_secret_entry.get().strip(),
            'tokenUrl': self.token_url_entry.get().strip(),
            'compareUrl': self.compare_url_entry.get().strip(),
            'saveDir': self.save_dir_entry.get().strip()
        }

    def validate_config(self):
        """验证配置是否完整"""
        config = self.get_config()
        if not config['appId']:
            messagebox.showwarning("提示", "请填写应用ID")
            return False
        if not config['appSecret']:
            messagebox.showwarning("提示", "请填写应用密钥")
            return False
        if not config['tokenUrl']:
            messagebox.showwarning("提示", "请填写Token接口地址")
            return False
        if not config['compareUrl']:
            messagebox.showwarning("提示", "请填写比对接口地址")
            return False
        if not config['saveDir']:
            messagebox.showwarning("提示", "请选择保存目录")
            return False
        return True

    def test_connection(self):
        """测试连接"""
        if not self.validate_config():
            return

        self.status_label.config(text="正在测试连接...", foreground='blue')
        self.test_btn.config(state='disabled')

        try:
            config = self.get_config()
            client = ApiClient(
                config['appId'],
                config['appSecret'],
                config['tokenUrl'],
                config['compareUrl']
            )

            success, message = client.test_connection()

            if success:
                self.status_label.config(text=message, foreground='green')
                messagebox.showinfo("成功", message)
            else:
                self.status_label.config(text=message, foreground='red')
                messagebox.showerror("失败", message)

        except Exception as e:
            self.status_label.config(text=f"测试失败: {str(e)}", foreground='red')
            messagebox.showerror("错误", f"测试失败: {str(e)}")

        self.test_btn.config(state='normal')

    def go_next(self):
        """下一步"""
        if not self.validate_config():
            return

        # 保存配置
        if self.save_config_var.get():
            self.config_manager.update(self.get_config())
            self.config_manager.save()

        # 调用下一步回调
        self.on_next_callback(self.get_config())