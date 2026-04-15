"""
国密加密模块
使用gmssl库实现SM3签名和SM4加密
支持Hex和Base64两种编码格式
"""

import base64
from gmssl import sm4, func, sm3


class CryptoService:
    """国密加密服务"""

    def __init__(self, key):
        """
        初始化加密服务
        :param key: 加密密钥（会自动填充/截断到16字节）
        """
        # 将密钥转换为list格式（gmssl要求）
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key

        # 截断或填充到16字节
        key_list = func.bytes_to_list(key_bytes[:16])
        while len(key_list) < 16:
            key_list.append(0)

        self.key = key_list

    def sm4_encrypt(self, plain_text, output_format='hex'):
        """
        SM4加密（ECB模式，PKCS7填充）
        :param plain_text: 明文字符串
        :param output_format: 输出格式 'hex' 或 'base64'
        :return: 编码后的密文
        """
        if isinstance(plain_text, str):
            plain_bytes = plain_text.encode('utf-8')
        else:
            plain_bytes = plain_text

        # 转换为list
        plain_list = func.bytes_to_list(plain_bytes)

        # PKCS7填充
        padded = func.pkcs7_padding(plain_list, 16)

        # 加密
        crypt_sm4 = sm4.CryptSM4()
        crypt_sm4.set_key(self.key, sm4.SM4_ENCRYPT)
        cipher_list = crypt_sm4.crypt_ecb(padded)

        # 转换为bytes
        cipher_bytes = func.list_to_bytes(cipher_list)

        # 根据格式编码
        if output_format == 'base64':
            return base64.b64encode(cipher_bytes).decode('utf-8')
        else:
            return cipher_bytes.hex()

    def sm4_decrypt(self, cipher_text):
        """
        SM4解密（ECB模式）
        :param cipher_text: Base64或Hex编码的密文
        :return: 明文字符串
        """
        # 判断编码格式并解码
        try:
            # 尝试Base64解码
            cipher_bytes = base64.b64decode(cipher_text)
        except Exception:
            # 如果Base64失败，尝试Hex解码
            cipher_bytes = bytes.fromhex(cipher_text)

        # 转换为list进行解密
        cipher_list = func.bytes_to_list(cipher_bytes)

        # 解密
        decrypt_sm4 = sm4.CryptSM4()
        decrypt_sm4.set_key(self.key, sm4.SM4_DECRYPT)
        decrypted_bytes = decrypt_sm4.crypt_ecb(cipher_list)

        # gmssl的crypt_ecb可能返回bytes或list
        if isinstance(decrypted_bytes, bytes):
            # 直接返回解码后的字符串（gmssl已处理填充）
            return decrypted_bytes.decode('utf-8')
        else:
            # 如果是list，需要转换并处理填充
            pad_len = decrypted_bytes[-1]
            decrypted_list = decrypted_bytes[:-pad_len]
            return func.list_to_bytes(decrypted_list).decode('utf-8')

    @staticmethod
    def sm3_sign(data):
        """
        SM3签名
        :param data: 待签名的字符串
        :return: 十六进制签名字符串
        """
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        return sm3.sm3_hash(func.bytes_to_list(data_bytes))

    @staticmethod
    def sign_for_request(app_secret, encrypt_data):
        """
        按照接口规范生成签名：SM3(appSecret + encryptData)
        :param app_secret: 应用密钥
        :param encrypt_data: 加密数据
        :return: 签名结果
        """
        sign_data = app_secret + encrypt_data
        return CryptoService.sm3_sign(sign_data)


# 便捷函数
def encrypt_data(plain_text, key, output_format='hex'):
    """加密数据的便捷函数"""
    crypto = CryptoService(key)
    return crypto.sm4_encrypt(plain_text, output_format)


def decrypt_data(cipher_text, key):
    """解密数据的便捷函数（支持Base64和Hex）"""
    crypto = CryptoService(key)
    return crypto.sm4_decrypt(cipher_text)


def sign_data(app_secret, encrypt_data):
    """生成签名的便捷函数"""
    return CryptoService.sign_for_request(app_secret, encrypt_data)