package com.example.aliveauth.security;

/**
 * 加密服务接口
 */
public interface CryptoService {

    /**
     * SM4加密 (ECB模式, PKCS7Padding)
     *
     * @param plainText 明文
     * @param key       密钥
     * @return 加密后的数据 (Base64编码)
     */
    String encryptBySM4(String plainText, String key);

    /**
     * SM4解密 (ECB模式, PKCS7Padding)
     *
     * @param cipherText 密文 (Base64或Hex编码)
     * @param key        密钥
     * @return 解密后的明文
     */
    String decryptBySM4(String cipherText, String key);

    /**
     * SM3签名
     * 签名规则: SM3(appSecret + encryptData)
     *
     * @param appSecret   应用密钥
     * @param encryptData 加密数据
     * @return 签名结果 (十六进制字符串)
     */
    String signBySM3(String appSecret, String encryptData);

    /**
     * SM3签名验证
     *
     * @param appSecret   应用密钥
     * @param encryptData 加密数据
     * @param sign        待验证的签名
     * @return 是否验证通过
     */
    boolean verifySM3Sign(String appSecret, String encryptData, String sign);
}