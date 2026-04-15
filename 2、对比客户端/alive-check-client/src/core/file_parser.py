"""
文件解析模块
处理ZJPV输入文件和ZJPC输出文件的解析与生成
"""

import os
import re
from datetime import datetime
from pathlib import Path


class ZJPVParser:
    """ZJPV文件解析器"""

    def __init__(self, filepath):
        """初始化解析器"""
        self.filepath = filepath
        self.filename = os.path.basename(filepath)

    def parse(self):
        """
        解析ZJPV文件
        :return: {
            'filename': 文件名,
            'persons': 人员列表,
            'record_count': 记录数,
            'header_line1': 第1行(文件标识),
            'header_line2': 第2行(TransactionHeader),
            'filepath': 文件路径
        }
        """
        persons = []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 保存文件头信息
            header_line1 = lines[0].strip() if len(lines) > 0 else '01'
            header_line2 = lines[1].strip() if len(lines) > 1 else '000000FFFFFFFFFFFFFFFFFFFF'

            # 解析记录数 (前6位)
            record_count_match = re.match(r'(\d{6})', header_line2)
            record_count = int(record_count_match.group(1)) if record_count_match else 0

            # 解析人员记录 (从第3行开始)
            for i in range(2, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue

                # 解析格式: 姓名 + 空格 + 身份证号
                parts = line.split()
                if len(parts) >= 2:
                    username = parts[0].strip()
                    idcard = parts[1].strip()
                    persons.append({
                        'username': username,
                        'idcard': idcard,
                        'line_num': i + 1  # 原始行号
                    })

            return {
                'filename': self.filename,
                'persons': persons,
                'record_count': record_count,
                'header_line1': header_line1,  # 文件标识
                'header_line2': header_line2,  # TransactionHeader
                'filepath': self.filepath
            }

        except Exception as e:
            raise Exception(f"解析文件失败: {str(e)}")

    def is_zjpv_file(self):
        """检查是否为ZJPV文件"""
        return self.filename.startswith('ZJPV')


class ZJPCWriter:
    """ZJPC文件写入器"""

    def __init__(self, filepath=None, save_dir=None, source_header=None):
        """
        初始化写入器
        :param filepath: 文件路径（可选）
        :param save_dir: 保存目录（可选）
        :param source_header: 源文件header信息 {'line1': '01', 'line2': '000005FFFFFFFFFFFFFFFFFFFF'}
        """
        self.filepath = filepath
        self.save_dir = save_dir
        self.source_header = source_header

    def generate_filename(self, date_str=None, sequence=1):
        """
        生成ZJPC文件名
        :param date_str: 日期字符串YYYYMMDD（可选）
        :param sequence: 序号（默认1）
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y%m%d')

        # 序号补齐到10位
        seq_str = str(sequence).zfill(10)
        return f'ZJPC{date_str}{seq_str}'

    def write(self, persons, filepath=None):
        """
        写入ZJPC文件（仅已故人员）
        :param persons: 已故人员列表 [{'username': '姓名', 'idcard': '身份证号'}, ...]
        :param filepath: 输出文件路径（可选）
        """
        output_path = filepath or self.filepath

        if not output_path:
            # 自动生成文件名
            filename = self.generate_filename()
            if self.save_dir:
                # 在保存目录下创建子文件夹 "2.生存已校验文件ZJPC"
                sub_dir = os.path.join(self.save_dir, "2.生存已校验文件ZJPC")
                os.makedirs(sub_dir, exist_ok=True)
                output_path = os.path.join(sub_dir, filename)
            else:
                output_path = filename

        try:
            # 构建文件内容
            lines = []

            # File Description Area (文件标识)
            if self.source_header and 'line1' in self.source_header:
                # 使用源文件的文件标识
                version = self.source_header['line1']
            else:
                version = 'SV'  # 默认版本

            lines.append(f'{version}\r\n')

            # TransactionHeader (交易头记录)
            if self.source_header and 'line2' in self.source_header:
                # 使用源文件的header格式，只更新记录数
                source_line2 = self.source_header['line2']
                # 提取保留域部分 (从第7位开始，共20位)
                reserved = source_line2[6:26] if len(source_line2) >= 26 else 'FFFFFFFFFFFFFFFFFFFF'
                # 更新记录数为实际已故人数
                record_count = str(len(persons)).zfill(6)
                header_line2 = f'{record_count}{reserved}'
            else:
                # 默认格式
                record_count = str(len(persons)).zfill(6)
                reserved = 'F' * 20
                header_line2 = f'{record_count}{reserved}'

            lines.append(f'{header_line2}\r\n')

            # File Record Area (记录区)
            for person in persons:
                # 姓名10位，右补空格
                username = person['username'][:10].ljust(10)
                # 身份证号20位，右补空格
                idcard = person['idcard'][:20].ljust(20)
                record = f'{username}{idcard}\r\n'
                lines.append(record)

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return output_path

        except Exception as e:
            raise Exception(f"写入文件失败: {str(e)}")


def find_zjpv_files(directory):
    """
    查找目录中的所有ZJPV文件
    :param directory: 目录路径
    :return: ZJPV文件路径列表
    """
    zjpv_files = []

    if not os.path.exists(directory):
        return zjpv_files

    for filename in os.listdir(directory):
        if filename.startswith('ZJPV'):
            filepath = os.path.join(directory, filename)
            zjpv_files.append(filepath)

    # 按文件名排序
    zjpv_files.sort()
    return zjpv_files


def parse_person_from_line(line):
    """
    从行文本解析人员信息
    :param line: 行文本
    :return: {'username': 姓名, 'idcard': 身份证号}
    """
    parts = line.strip().split()
    if len(parts) >= 2:
        return {
            'username': parts[0].strip(),
            'idcard': parts[1].strip()
        }
    return None