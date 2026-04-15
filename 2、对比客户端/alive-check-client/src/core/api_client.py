"""
接口调用客户端
负责调用生存认证接口，处理加密签名流程
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
from core.crypto import encrypt_data, decrypt_data, sign_data


class ApiClient:
    """生存认证接口客户端"""

    def __init__(self, app_id, app_secret, token_url, compare_url):
        """
        初始化客户端
        :param app_id: 应用ID
        :param app_secret: 应用密钥
        :param token_url: Token接口地址
        :param compare_url: 生存比对接口地址
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_url = token_url
        self.compare_url = compare_url
        self.token = None
        self.token_expire_time = None

    def _build_request_body(self, content):
        """
        构建符合接口规范的请求体
        :param content: 待加密的请求内容（JSON字符串或对象）
        """
        if isinstance(content, dict) or isinstance(content, list):
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = content

        # SM4加密
        encrypt_data_str = encrypt_data(content_str, self.app_secret)

        # SM3签名
        sign = sign_data(self.app_secret, encrypt_data_str)

        # 构建请求体
        request_body = {
            'appId': self.app_id,
            'encryptType': 'SM4',
            'signType': 'SM3',
            'encryptData': encrypt_data_str,
            'sign': sign,
            'timestamp': str(int(__import__('time').time() * 1000)),
            'version': '1.0.0'
        }

        return json.dumps(request_body, ensure_ascii=False)

    def _decrypt_response(self, response_json):
        """
        解密响应数据
        :param response_json: 响应JSON对象
        :return: 解密后的数据
        """
        if response_json.get('respCode') != 0:
            raise Exception(f"接口返回错误: {response_json.get('respMsg', '未知错误')}")

        encrypt_data = response_json.get('encryptData')
        if not encrypt_data:
            raise Exception("响应数据为空")

        return decrypt_data(encrypt_data, self.app_secret)

    def generate_token(self):
        """
        生成Token
        :return: Token响应数据
        """
        # 构建请求内容
        content = {
            'appId': self.app_id,
            'appSecret': self.app_secret
        }

        request_body = self._build_request_body(content)

        # 发送请求
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(self.token_url, data=request_body, headers=headers)

        if response.status_code != 200:
            raise Exception(f"请求失败: HTTP {response.status_code}")

        response_json = response.json()

        # 解密响应
        decrypted = self._decrypt_response(response_json)
        token_data = json.loads(decrypted)

        # 保存Token
        self.token = token_data.get('token')
        self.token_expire_time = token_data.get('createTime') + token_data.get('expiresIn') * 1000

        return token_data

    def is_token_valid(self):
        """检查Token是否有效"""
        if not self.token:
            return False

        import time
        if self.token_expire_time and time.time() * 1000 < self.token_expire_time:
            return True

        return False

    def ensure_token(self):
        """确保Token有效，必要时重新获取"""
        if not self.is_token_valid():
            self.generate_token()
        return self.token

    def alive_compare(self, persons):
        """
        生存比对接口
        :param persons: 人员列表 [{'idcard': '身份证号', 'username': '姓名'}, ...]
        :return: 比对结果列表
        """
        # 确保Token有效
        token = self.ensure_token()

        # 构建请求内容
        request_body = self._build_request_body(persons)

        # 发送请求（带Token请求头）
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'token': token
        }
        response = requests.post(self.compare_url, data=request_body, headers=headers)

        if response.status_code != 200:
            raise Exception(f"请求失败: HTTP {response.status_code}")

        response_json = response.json()

        # 解密响应
        decrypted = self._decrypt_response(response_json)
        compare_results = json.loads(decrypted)

        return compare_results

    def test_connection(self):
        """
        测试连接是否正常
        :return: (success, message)
        """
        try:
            token_data = self.generate_token()
            return True, f"连接成功，Token有效期: {token_data.get('expiresIn')}秒"
        except Exception as e:
            return False, f"连接失败: {str(e)}"