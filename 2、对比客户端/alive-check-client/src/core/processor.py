"""
批量处理模块
负责处理多个ZJPV文件，调用接口比对，输出已故人员ZJPC文件
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime
from core.file_parser import ZJPVParser, ZJPCWriter, find_zjpv_files


class BatchProcessor:
    """批量处理器"""

    def __init__(self, api_client, save_dir):
        """
        初始化处理器
        :param api_client: API客户端实例
        :param save_dir: 输出文件保存目录
        """
        self.api_client = api_client
        self.save_dir = save_dir
        self.running = False
        self.current_file = None
        self.processed_count = 0
        self.deceased_count = 0
        self.total_count = 0

    def process_directory(self, input_dir, progress_callback=None, log_callback=None):
        """
        处理目录中的所有ZJPV文件
        :param input_dir: 输入目录
        :param progress_callback: 进度回调函数
        :param log_callback: 日志回调函数
        :return: 处理结果统计
        """
        self.running = True
        self.processed_count = 0
        self.deceased_count = 0

        # 查找所有ZJPV文件
        zjpv_files = find_zjpv_files(input_dir)

        if not zjpv_files:
            if log_callback:
                log_callback("未找到ZJPV文件")
            return None

        # 确保保存目录存在
        os.makedirs(self.save_dir, exist_ok=True)

        # 统计总人数，并保存源文件header信息
        total_persons = 0
        all_persons = []
        source_header = None  # 保存第一个文件的header信息

        for filepath in zjpv_files:
            parser = ZJPVParser(filepath)
            file_data = parser.parse()

            # 保存第一个文件的header信息，用于输出文件保持一致
            if source_header is None:
                source_header = {
                    'line1': file_data.get('header_line1', '01'),
                    'line2': file_data.get('header_line2', '000000FFFFFFFFFFFFFFFFFFFF')
                }

            file_persons = []
            for person in file_data['persons']:
                person_data = person.copy()
                person_data['source_filename'] = file_data['filename']
                file_persons.append(person_data)

            total_persons += len(file_persons)
            all_persons.extend(file_persons)

        self.total_count = total_persons

        if log_callback:
            log_callback(f"共发现 {len(zjpv_files)} 个文件，总计 {total_persons} 人")
            log_callback(f"源文件标识: {source_header['line1']}")
            log_callback(f"源文件Header: {source_header['line2']}")

        # 按批次调用接口（每批100人）
        batch_size = 100
        deceased_persons = []
        processed_files = []

        try:
            # 先生成Token
            if log_callback:
                log_callback("正在获取Token...")
            self.api_client.generate_token()
            if log_callback:
                log_callback("Token获取成功")

            # 批量比对
            all_results = []
            for i in range(0, len(all_persons), batch_size):
                if not self.running:
                    if log_callback:
                        log_callback("处理已停止")
                    break

                batch = all_persons[i:i + batch_size]

                batch_files = {person.get('source_filename') for person in batch if person.get('source_filename')}
                if len(batch_files) == 1:
                    self.current_file = next(iter(batch_files))
                elif batch_files:
                    first_file = batch[0].get('source_filename', '未知文件')
                    self.current_file = f"{first_file} 等{len(batch_files)}个文件"
                else:
                    self.current_file = None

                # 构建请求
                request_persons = [{'idcard': p['idcard'], 'username': p['username']} for p in batch]

                # 调用接口
                results = self.api_client.alive_compare(request_persons)
                all_results.extend(results)

                # 更新进度
                self.processed_count = min(i + batch_size, len(all_persons))

                # 收集已故人员
                for result in results:
                    if result.get('aliveStatus') == 'DEAD':
                        deceased_persons.append({
                            'username': result.get('username'),
                            'idcard': result.get('idcard')
                        })
                        self.deceased_count += 1

                # 回调进度
                if progress_callback:
                    progress = self.processed_count / self.total_count if self.total_count > 0 else 0
                    progress_callback(progress, self.current_file, self.processed_count, self.deceased_count)

                if log_callback:
                    log_callback(f"已处理 {self.processed_count}/{self.total_count} 人，已故 {self.deceased_count} 人")

                # 短暂延迟避免请求过快
                time.sleep(0.1)

            # 写入已故人员文件，使用源文件的header格式
            if deceased_persons and self.running:
                if log_callback:
                    log_callback("正在生成已故人员文件...")

                # 使用源文件的header信息创建写入器
                writer = ZJPCWriter(
                    save_dir=self.save_dir,
                    source_header=source_header  # 传递源文件header
                )
                output_path = writer.write(deceased_persons)

                if log_callback:
                    log_callback(f"已故人员文件已保存: {output_path}")

                processed_files.append(output_path)

            # 返回结果
            return {
                'total_files': len(zjpv_files),
                'total_persons': total_persons,
                'processed_persons': self.processed_count,
                'deceased_persons': self.deceased_count,
                'output_file': output_path if deceased_persons else None
            }

        except Exception as e:
            if log_callback:
                log_callback(f"处理出错: {str(e)}")
            raise e

    def stop(self):
        """停止处理"""
        self.running = False
