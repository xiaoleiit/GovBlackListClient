package com.example.aliveauth.dto.request;

import lombok.Data;

/**
 * 统一请求报文DTO
 */
@Data
public class OpenApiRequest {
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
     * SM4加密后的数据 (Base64或Hex编码)
     */
    private String encryptData;

    /**
     * SM3签名数据
     */
    private String sign;

    /**
     * 时间戳 (Unix时间戳字符串)
     */
    private String timestamp;

    /**
     * 接口版本
     */
    private String version;
}