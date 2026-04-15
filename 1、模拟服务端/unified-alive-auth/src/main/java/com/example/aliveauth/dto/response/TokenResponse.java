package com.example.aliveauth.dto.response;

import lombok.Data;

/**
 * Token响应内容 (加密前)
 */
@Data
public class TokenResponse {
    /**
     * Token值
     */
    private String token;

    /**
     * 过期时间(秒)
     */
    private Long expiresIn;

    /**
     * 创建时间戳
     */
    private Long createTime;
}