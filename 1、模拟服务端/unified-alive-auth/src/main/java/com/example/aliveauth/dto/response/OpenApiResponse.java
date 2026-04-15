package com.example.aliveauth.dto.response;

import lombok.Data;

/**
 * 统一响应报文DTO
 */
@Data
public class OpenApiResponse {
    /**
     * 应用ID
     */
    private String appId;

    /**
     * 加密类型 (SM4)
     */
    private String encryptType;

    /**
     * 签名方式 (SM3)
     */
    private String signType;

    /**
     * SM4加密后的数据
     */
    private String encryptData;

    /**
     * SM3签名数据
     */
    private String sign;

    /**
     * 时间戳
     */
    private String timestamp;

    /**
     * 接口版本
     */
    private String version;

    /**
     * 响应协议码 (0-成功)
     */
    private Integer respCode;

    /**
     * 响应说明
     */
    private String respMsg;

    /**
     * 构建成功响应
     */
    public static OpenApiResponse success(String appId, String encryptData, String sign) {
        OpenApiResponse response = new OpenApiResponse();
        response.setAppId(appId);
        response.setEncryptType("SM4");
        response.setSignType("SM3");
        response.setEncryptData(encryptData);
        response.setSign(sign);
        response.setTimestamp(String.valueOf(System.currentTimeMillis()));
        response.setVersion("1.0.0");
        response.setRespCode(0);
        response.setRespMsg("操作成功");
        return response;
    }

    /**
     * 构建失败响应
     */
    public static OpenApiResponse fail(Integer respCode, String respMsg) {
        OpenApiResponse response = new OpenApiResponse();
        response.setEncryptType("SM4");
        response.setSignType("SM3");
        response.setTimestamp(String.valueOf(System.currentTimeMillis()));
        response.setVersion("1.0.0");
        response.setRespCode(respCode);
        response.setRespMsg(respMsg);
        return response;
    }
}