"""
结果对话框
比对完成后显示友好的提示
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform


class ResultDialog(tk.Toplevel):
    """结果对话框"""

    def __init__(self, parent, result):
        """
        初始化对话框
        :param parent: 父窗口
        :param result: 处理结果 {'total_persons': 总人数, 'deceased_persons': 已故人数, 'output_file': 输出文件路径}
        """
        super().__init__(parent)
        self.result = result

        self.title("比对完成")
        self.geometry("400x300")
        self.resizable(False, False)

        # 居中显示
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.close)

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self, text="比对完成", font=('Arial', 18, 'bold'), foreground='green')
        title_label.pack(pady=20)

        # 结果信息
        info_frame = ttk.Frame(self)
        info_frame.pack(pady=20, fill='x')

        # 总人数
        total_text = f"本次共处理 {self.result['total_persons']} 位人员"
        ttk.Label(info_frame, text=total_text, font=('Arial', 12)).pack(pady=5)

        # 已故人数
        deceased_count = self.result['deceased_persons']
        if deceased_count > 0:
            deceased_text = f"发现 {deceased_count} 位已故人员"
            deceased_label = ttk.Label(info_frame, text=deceased_text, font=('Arial', 14), foreground='red')
            deceased_label.pack(pady=10)

            # 输出文件
            if self.result['output_file']:
                file_frame = ttk.Frame(self)
                file_frame.pack(pady=10)

                ttk.Label(file_frame, text="已为您保存到:", font=('Arial', 10)).pack()

                output_path = self.result['output_file']
                # 只显示文件名，完整路径在点击查看时显示
                filename = os.path.basename(output_path)
                ttk.Label(file_frame, text=filename, font=('Arial', 12, 'bold')).pack(pady=5)
        else:
            # 没有已故人员
            ttk.Label(info_frame, text="未发现已故人员", font=('Arial', 14), foreground='green').pack(pady=10)

        # 提示文字（友好语气）
        if deceased_count > 0:
            tip_text = "已故人员信息已妥善保存，请及时处理后续事宜"
        else:
            tip_text = "所有人员状态正常，感谢您的关注"

        ttk.Label(self, text=tip_text, font=('Arial', 10), foreground='gray').pack(pady=10)

        # 按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        # 查看文件按钮（如果有输出文件）
        if deceased_count > 0 and self.result['output_file']:
            view_btn = ttk.Button(button_frame, text="查看文件", command=self.view_file, width=12)
            view_btn.pack(side='left', padx=10)

        close_btn = ttk.Button(button_frame, text="关闭", command=self.close, width=12)
        close_btn.pack(side='left', padx=10)

    def view_file(self):
        """查看输出文件"""
        output_file = self.result['output_file']

        if not output_file or not os.path.exists(output_file):
            messagebox.showwarning("提示", "文件不存在")
            return

        # 打开文件夹并选中文件
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', '/select,', output_file])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-R', output_file])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(output_file)])
        except Exception as e:
            messagebox.showinfo("文件路径", f"文件位置: {output_file}")

    def close(self):
        """关闭对话框"""
        self.destroy()