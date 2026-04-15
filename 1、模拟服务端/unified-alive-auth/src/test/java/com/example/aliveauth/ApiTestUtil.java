package com.example.aliveauth;

import cn.hutool.core.util.IdUtil;
import cn.hutool.crypto.SmUtil;
import cn.hutool.crypto.symmetric.SM4;
import cn.hutool.json.JSONUtil;

import java.nio.charset.StandardCharsets;

/**
 * 接口测试工具类
 * 用于生成符合接口规范的请求数据
 */
public class ApiTestUtil {

    /**
     * 模拟应用配置
     */
    private static final String APP_ID = "APP001";
    private static final String APP_SECRET = "secret001abcdef";

    /**
     * SM4加密 (生成符合接口规范的encryptData)
     */
    public static String encryptBySM4(String plainText, String key) {
        byte[] keyBytes = paddingKey(key);
        SM4 sm4 = new SM4(keyBytes);
        return sm4.encryptBase64(plainText);
    }

    /**
     * SM4解密
     */
    public static String decryptBySM4(String cipherText, String key) {
        byte[] keyBytes = paddingKey(key);
        SM4 sm4 = new SM4(keyBytes);
        return sm4.decryptStr(cipherText);
    }

    /**
     * SM3签名 (生成符合接口规范的sign)
     */
    public static String signBySM3(String appSecret, String encryptData) {
        return SmUtil.sm3(appSecret + encryptData);
    }

    /**
     * 生成生成Token接口的请求数据
     */
    public static String buildTokenRequest() {
        // 构建加密前的请求内容
        String requestContent = JSONUtil.toJsonStr(new TokenRequestData(APP_ID, APP_SECRET));

        // SM4加密
        String encryptData = encryptBySM4(requestContent, APP_SECRET);

        // SM3签名
        String sign = signBySM3(APP_SECRET, encryptData);

        // 构建完整请求
        OpenApiRequestData request = new OpenApiRequestData();
        request.setAppId(APP_ID);
        request.setEncryptType("SM4");
        request.setSignType("SM3");
        request.setEncryptData(encryptData);
        request.setSign(sign);
        request.setTimestamp(String.valueOf(System.currentTimeMillis()));
        request.setVersion("1.0.0");

        return JSONUtil.toJsonStr(request);
    }

    /**
     * 生成生存比对接口的请求数据
     */
    public static String buildAliveCompareRequest(String token) {
        // 构建加密前的请求内容 (数组格式)
        String requestContent = JSONUtil.toJsonStr(new AliveCompareRequestData[]{
                new AliveCompareRequestData("110101199001011234", "张三"),
                new AliveCompareRequestData("110101198505052345", "李四")
        });

        // SM4加密
        String encryptData = encryptBySM4(requestContent, APP_SECRET);

        // SM3签名
        String sign = signBySM3(APP_SECRET, encryptData);

        // 构建完整请求
        OpenApiRequestData request = new OpenApiRequestData();
        request.setAppId(APP_ID);
        request.setEncryptType("SM4");
        request.setSignType("SM3");
        request.setEncryptData(encryptData);
        request.setSign(sign);
        request.setTimestamp(String.valueOf(System.currentTimeMillis()));
        request.setVersion("1.0.0");

        return JSONUtil.toJsonStr(request);
    }

    /**
     * 解密响应数据
     */
    public static String decryptResponse(String encryptData) {
        return decryptBySM4(encryptData, APP_SECRET);
    }

    /**
     * 密钥填充到16字节
     */
    private static byte[] paddingKey(String key) {
        byte[] keyBytes = new byte[16];
        byte[] srcBytes = key.getBytes(StandardCharsets.UTF_8);
        int copyLength = Math.min(srcBytes.length, 16);
        System.arraycopy(srcBytes, 0, keyBytes, 0, copyLength);
        return keyBytes;
    }

    // ===== 内部数据类 =====

    static class TokenRequestData {
        private String appId;
        private String appSecret;

        public TokenRequestData(String appId, String appSecret) {
            this.appId = appId;
            this.appSecret = appSecret;
        }

        public String getAppId() { return appId; }
        public String getAppSecret() { return appSecret; }
    }

    static class AliveCompareRequestData {
        private String idcard;
        private String username;

        public AliveCompareRequestData(String idcard, String username) {
            this.idcard = idcard;
            this.username = username;
        }

        public String getIdcard() { return idcard; }
        public String getUsername() { return username; }
    }

    static class OpenApiRequestData {
        private String appId;
        private String encryptType;
        private String signType;
        private String encryptData;
        private String sign;
        private String timestamp;
        private String version;

        // getters and setters
        public String getAppId() { return appId; }
        public void setAppId(String appId) { this.appId = appId; }
        public String getEncryptType() { return encryptType; }
        public void setEncryptType(String encryptType) { this.encryptType = encryptType; }
        public String getSignType() { return signType; }
        public void setSignType(String signType) { this.signType = signType; }
        public String getEncryptData() { return encryptData; }
        public void setEncryptData(String encryptData) { this.encryptData = encryptData; }
        public String getSign() { return sign; }
        public void setSign(String sign) { this.sign = sign; }
        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
    }

    // ===== main方法用于测试 =====

    public static void main(String[] args) {
        System.out.println("===== 生成Token接口请求数据 =====");
        String tokenRequest = buildTokenRequest();
        System.out.println(tokenRequest);
        System.out.println();

        System.out.println("===== 生存比对接口请求数据 =====");
        String aliveCompareRequest = buildAliveCompareRequest("test-token-placeholder");
        System.out.println(aliveCompareRequest);
        System.out.println();

        System.out.println("===== curl命令示例 =====");
        System.out.println("生成Token:");
        System.out.println("curl -X POST http://localhost:8080/openapi/stoken -H \"Content-Type: application/json\" -d '" + tokenRequest + "'");
        System.out.println();
        System.out.println("生存比对:");
        System.out.println("curl -X POST http://localhost:8080/openapi/aliveCompare -H \"Content-Type: application/json\" -H \"token: <your-token>\" -d '" + aliveCompareRequest + "'");
    }
}