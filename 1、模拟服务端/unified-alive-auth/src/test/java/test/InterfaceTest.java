package test;

import cn.hutool.crypto.SmUtil;
import cn.hutool.crypto.symmetric.SM4;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import java.nio.charset.StandardCharsets;

public class InterfaceTest {
    private static final String APP_ID = "APP001";
    private static final String APP_SECRET = "secret001abcdef";
    private static final String BASE_URL = "http://localhost:8080";

    public static void main(String[] args) {
        System.out.println("========== 测试5.1 生成Token接口 ==========\n");

        // 1. 构建请求内容
        JSONObject tokenContent = new JSONObject();
        tokenContent.set("appId", APP_ID);
        tokenContent.set("appSecret", APP_SECRET);
        System.out.println("原始请求内容: " + tokenContent.toString());

        // 2. SM4加密
        String encryptData = encryptSM4(tokenContent.toString());

        // 3. SM3签名
        String sign = SmUtil.sm3(APP_SECRET + encryptData);

        // 4. 构建完整请求
        JSONObject requestBody = new JSONObject();
        requestBody.set("appId", APP_ID);
        requestBody.set("encryptType", "SM4");
        requestBody.set("signType", "SM3");
        requestBody.set("encryptData", encryptData);
        requestBody.set("sign", sign);
        requestBody.set("timestamp", String.valueOf(System.currentTimeMillis()));
        requestBody.set("version", "1.0.0");

        System.out.println("请求报文:\n" + requestBody.toStringPretty() + "\n");

        // 5. 发送请求
        String responseBody = HttpUtil.post(BASE_URL + "/openapi/stoken", requestBody.toString());
        System.out.println("响应报文:\n" + JSONUtil.parseObj(responseBody).toStringPretty() + "\n");

        // 6. 解密响应
        JSONObject responseJson = JSONUtil.parseObj(responseBody);
        String responseEncryptData = responseJson.getStr("encryptData");
        if (responseEncryptData != null) {
            String decryptedToken = decryptSM4(responseEncryptData);
            System.out.println("解密后响应:\n" + JSONUtil.parseObj(decryptedToken).toStringPretty() + "\n");

            String token = JSONUtil.parseObj(decryptedToken).getStr("token");
            System.out.println("获取到Token: " + token + "\n");

            // ===== 测试生存比对接口 =====
            testAliveCompare(token);
        }

        System.out.println("========== 测试完成 ==========");
    }

    private static void testAliveCompare(String token) {
        System.out.println("========== 测试5.4 生存比对接口 ==========\n");

        // 1. 构建比对请求内容(数组格式)
        JSONArray compareContent = new JSONArray();
        compareContent.add(new JSONObject().set("idcard", "110101199001011234").set("username", "张三"));
        compareContent.add(new JSONObject().set("idcard", "110101198505052345").set("username", "李四"));
        compareContent.add(new JSONObject().set("idcard", "310101199203033456").set("username", "王五"));
        compareContent.add(new JSONObject().set("idcard", "999999999999999999").set("username", "不存在的人"));

        System.out.println("原始请求内容: " + compareContent.toString());

        // 2. SM4加密
        String encryptData = encryptSM4(compareContent.toString());

        // 3. SM3签名
        String sign = SmUtil.sm3(APP_SECRET + encryptData);

        // 4. 构建完整请求
        JSONObject requestBody = new JSONObject();
        requestBody.set("appId", APP_ID);
        requestBody.set("encryptType", "SM4");
        requestBody.set("signType", "SM3");
        requestBody.set("encryptData", encryptData);
        requestBody.set("sign", sign);
        requestBody.set("timestamp", String.valueOf(System.currentTimeMillis()));
        requestBody.set("version", "1.0.0");

        System.out.println("请求报文:\n" + requestBody.toStringPretty() + "\n");

        // 5. 发送请求(带Token)
        String responseBody = HttpUtil.createPost(BASE_URL + "/openapi/aliveCompare")
                .header("token", token)
                .body(requestBody.toString())
                .execute()
                .body();
        System.out.println("响应报文:\n" + JSONUtil.parseObj(responseBody).toStringPretty() + "\n");

        // 6. 解密响应
        JSONObject responseJson = JSONUtil.parseObj(responseBody);
        String responseEncryptData = responseJson.getStr("encryptData");
        if (responseEncryptData != null) {
            String decryptedCompare = decryptSM4(responseEncryptData);
            System.out.println("解密后响应(比对结果):\n" + JSONUtil.parseArray(decryptedCompare).toStringPretty() + "\n");
        }
    }

    private static String encryptSM4(String plainText) {
        byte[] keyBytes = paddingKey(APP_SECRET);
        SM4 sm4 = new SM4(keyBytes);
        return sm4.encryptBase64(plainText);
    }

    private static String decryptSM4(String cipherText) {
        byte[] keyBytes = paddingKey(APP_SECRET);
        SM4 sm4 = new SM4(keyBytes);
        return sm4.decryptStr(cipherText);
    }

    private static byte[] paddingKey(String key) {
        byte[] keyBytes = new byte[16];
        byte[] srcBytes = key.getBytes(StandardCharsets.UTF_8);
        int copyLength = Math.min(srcBytes.length, 16);
        System.arraycopy(srcBytes, 0, keyBytes, 0, copyLength);
        return keyBytes;
    }
}