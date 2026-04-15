package com.example.aliveauth.dto.request;

import lombok.Data;

/**
 * 生成Token请求内容 (加密前)
 */
@Data
public class TokenRequest {
    /**
     * 应用ID
     */
    private String appId;

    /**
     * 应用密钥
     */
    private String appSecret;
}