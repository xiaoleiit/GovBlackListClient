"""
配置管理模块
负责用户配置的读取、保存和管理
"""

import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG_DIR = Path.home() / '.alive-check'
    DEFAULT_CONFIG_FILE = 'config.json'

    # 默认配置模板
    DEFAULT_CONFIG = {
        'appId': '',
        'appSecret': '',
        'tokenUrl': 'http://localhost:8080/openapi/stoken',
        'compareUrl': 'http://localhost:8080/openapi/aliveCompare',
        'saveDir': str(Path.home() / 'Documents' / '生存比对结果')
    }

    def __init__(self, config_dir=None):
        """初始化配置管理器"""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = self.DEFAULT_CONFIG_DIR

        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILE
        self.config = self.DEFAULT_CONFIG.copy()

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 尝试加载已保存的配置
        self.load()

    def load(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 合并保存的配置（保留默认值作为fallback）
                    for key in self.DEFAULT_CONFIG:
                        if key in saved_config:
                            self.config[key] = saved_config[key]
                return True
            except Exception as e:
                print(f"加载配置失败: {e}")
                return False
        return False

    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key):
        """获取配置项"""
        return self.config.get(key, self.DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value

    def update(self, config_dict):
        """批量更新配置"""
        for key, value in config_dict.items():
            self.config[key] = value

    def is_configured(self):
        """检查是否已配置必要参数"""
        required_keys = ['appId', 'appSecret', 'tokenUrl', 'compareUrl', 'saveDir']
        for key in required_keys:
            if not self.config.get(key):
                return False
        return True

    def get_config_path(self):
        """获取配置文件路径"""
        return str(self.config_file)

    def clear(self):
        """清除配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        if self.config_file.exists():
            self.config_file.unlink()