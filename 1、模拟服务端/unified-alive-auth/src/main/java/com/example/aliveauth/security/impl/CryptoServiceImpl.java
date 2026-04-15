package com.example.aliveauth.security.impl;

import cn.hutool.core.util.HexUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.crypto.SmUtil;
import cn.hutool.crypto.symmetric.SM4;
import com.example.aliveauth.security.CryptoService;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

/**
 * 加密服务实现类
 * 使用Hutool库实现SM3签名和SM4加密
 */
@Service
public class CryptoServiceImpl implements CryptoService {

    /**
     * SM4加密 (ECB模式, PKCS7Padding)
     * Hutool的SM4默认使用ECB模式和PKCS7Padding
     */
    @Override
    public String encryptBySM4(String plainText, String key) {
        byte[] keyBytes = paddingKey(key);
        SM4 sm4 = new SM4(keyBytes);
        // 返回Base64编码的密文
        return sm4.encryptBase64(plainText);
    }

    /**
     * SM4解密 (ECB模式, PKCS7Padding)
     */
    @Override
    public String decryptBySM4(String cipherText, String key) {
        byte[] keyBytes = paddingKey(key);
        SM4 sm4 = new SM4(keyBytes);

        // 支持Base64或Hex格式的密文
        if (isHexString(cipherText)) {
            return sm4.decryptStr(HexUtil.decodeHex(cipherText));
        } else {
            return sm4.decryptStr(cipherText);
        }
    }

    /**
     * SM3签名
     * 签名规则: SM3(appSecret + encryptData)
     */
    @Override
    public String signBySM3(String appSecret, String encryptData) {
        String dataToSign = appSecret + encryptData;
        return SmUtil.sm3(dataToSign);
    }

    /**
     * SM3签名验证
     */
    @Override
    public boolean verifySM3Sign(String appSecret, String encryptData, String sign) {
        String expectedSign = signBySM3(appSecret, encryptData);
        return StrUtil.equalsIgnoreCase(expectedSign, sign);
    }

    /**
     * 密钥填充/截断到16字节 (SM4密钥要求128位)
     */
    private byte[] paddingKey(String key) {
        byte[] keyBytes = new byte[16];
        byte[] srcBytes = key.getBytes(StandardCharsets.UTF_8);
        int copyLength = Math.min(srcBytes.length, 16);
        System.arraycopy(srcBytes, 0, keyBytes, 0, copyLength);
        return keyBytes;
    }

    /**
     * 判断字符串是否为十六进制格式
     */
    private boolean isHexString(String str) {
        if (StrUtil.isEmpty(str)) {
            return false;
        }
        return str.matches("^[0-9a-fA-F]+$");
    }
}