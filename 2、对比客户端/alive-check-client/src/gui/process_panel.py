"""
处理面板
第二步：选择待校验文件夹，显示进度，执行比对
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from core.api_client import ApiClient
from core.processor import BatchProcessor


class ProcessPanel(ttk.Frame):
    """处理面板"""

    def __init__(self, parent, config, on_back_callback, on_complete_callback):
        """
        初始化处理面板
        :param parent: 父容器
        :param config: 配置字典
        :param on_back_callback: 返回配置回调
        :param on_complete_callback: 完成回调
        """
        super().__init__(parent)
        self.config = config
        self.on_back_callback = on_back_callback
        self.on_complete_callback = on_complete_callback
        self.processor = None
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # 标题
        title_label = ttk.Label(self, text="选择待校验文件夹", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # 文件夹选择区域
        dir_frame = ttk.Frame(self)
        dir_frame.grid(row=1, column=0, padx=40, pady=10, sticky='ew')
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="文件夹:", font=('Arial', 12)).grid(row=0, column=0, sticky='w')
        self.dir_entry = ttk.Entry(dir_frame, width=35, font=('Arial', 12))
        self.dir_entry.grid(row=0, column=1, padx=10, sticky='ew')
        self.select_btn = ttk.Button(dir_frame, text="选择...", command=self.select_directory)
        self.select_btn.grid(row=0, column=2, sticky='e')

        # 进度区域
        progress_frame = ttk.LabelFrame(self, text="处理进度", padding=10)
        progress_frame.grid(row=2, column=0, padx=40, pady=(10, 15), sticky='ew')
        progress_frame.columnconfigure(0, weight=1)

        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(pady=10, fill='x')

        # 进度文本
        self.progress_label = ttk.Label(progress_frame, text="进度: 0%", font=('Arial', 12))
        self.progress_label.pack()

        # 当前文件
        self.file_label = ttk.Label(progress_frame, text="当前文件: 无", font=('Arial', 10))
        self.file_label.pack(pady=5)

        # 统计信息
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(pady=10)

        self.processed_label = ttk.Label(stats_frame, text="已处理: 0人", font=('Arial', 12))
        self.processed_label.pack(side='left', padx=20)

        self.deceased_label = ttk.Label(stats_frame, text="已故: 0人", font=('Arial', 12), foreground='red')
        self.deceased_label.pack(side='left', padx=20)

        # 日志区域
        log_frame = ttk.LabelFrame(self, text="处理日志", padding=10)
        log_frame.grid(row=3, column=0, padx=40, pady=(0, 12), sticky='nsew')
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10, font=('Arial', 10), wrap='word')
        self.log_text.grid(row=0, column=0, sticky='nsew')

        log_scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.grid(row=0, column=1, sticky='ns')

        # 按钮区域 - 固定在底部
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, padx=40, pady=(0, 20), sticky='ew')

        self.back_btn = ttk.Button(button_frame, text="返回配置", command=self.go_back, width=12)
        self.back_btn.pack(side='right', padx=10)

        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_process, width=12, state='disabled')
        self.stop_btn.pack(side='right', padx=10)

        self.start_btn = ttk.Button(button_frame, text="开始比对", command=self.start_process, width=12)
        self.start_btn.pack(side='right', padx=10)

    def select_directory(self):
        """选择待校验文件夹"""
        current_dir = self.dir_entry.get() or os.path.expanduser('~')
        selected_dir = filedialog.askdirectory(initialdir=current_dir, title="选择待校验文件夹")
        if selected_dir:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_dir)

    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def update_progress(self, progress, filename, processed, deceased):
        """更新进度显示"""
        self.progress_var.set(progress * 100)
        self.progress_label.config(text=f"进度: {int(progress * 100)}%")
        if filename:
            self.file_label.config(text=f"当前文件: {filename}")
        self.processed_label.config(text=f"已处理: {processed}人")
        self.deceased_label.config(text=f"已故: {deceased}人")

    def start_process(self):
        """开始处理"""
        input_dir = self.dir_entry.get().strip()

        if not input_dir:
            messagebox.showwarning("提示", "请选择待校验文件夹")
            return

        if not os.path.exists(input_dir):
            messagebox.showwarning("提示", "选择的文件夹不存在")
            return

        # 重置状态
        self.progress_var.set(0)
        self.progress_label.config(text="进度: 0%")
        self.file_label.config(text="当前文件: 无")
        self.processed_label.config(text="已处理: 0人")
        self.deceased_label.config(text="已故: 0人")
        self.log_text.delete(1.0, tk.END)

        # 更新按钮状态
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.back_btn.config(state='disabled')

        self.running = True

        # 在线程中执行处理 (注意args必须是tuple，需要逗号)
        thread = threading.Thread(target=self._process_thread, args=(input_dir,))
        thread.start()

    def _process_thread(self, input_dir):
        """处理线程"""
        try:
            # 先打印日志
            self.after(0, lambda: self.log(f"开始处理目录: {input_dir}"))

            # 创建API客户端
            client = ApiClient(
                self.config['appId'],
                self.config['appSecret'],
                self.config['tokenUrl'],
                self.config['compareUrl']
            )

            # 创建处理器
            self.processor = BatchProcessor(client, self.config['saveDir'])

            # 执行处理
            result = self.processor.process_directory(
                input_dir,
                progress_callback=self._progress_callback,
                log_callback=self._log_callback
            )

            if result and self.running:
                # 处理完成
                self.after(0, lambda: self._on_complete(result))

        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))

    def _progress_callback(self, progress, filename, processed, deceased):
        """进度回调"""
        self.after(0, lambda: self.update_progress(progress, filename, processed, deceased))

    def _log_callback(self, message):
        """日志回调"""
        self.after(0, lambda: self.log(message))

    def _on_complete(self, result):
        """处理完成"""
        # 更新按钮状态
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.back_btn.config(state='normal')

        # 调用完成回调
        self.on_complete_callback(result)

    def _on_error(self, error):
        """处理出错"""
        self.log(f"错误: {error}")
        messagebox.showerror("错误", error)

        # 更新按钮状态
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.back_btn.config(state='normal')

    def stop_process(self):
        """停止处理"""
        if self.processor:
            self.processor.stop()
        self.running = False
        self.log("正在停止处理...")

        # 更新按钮状态
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.back_btn.config(state='normal')

    def go_back(self):
        """返回配置"""
        self.on_back_callback()
