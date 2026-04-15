package com.example.aliveauth.dto.request;

import lombok.Data;

/**
 * 生存比对请求内容 (加密前)
 */
@Data
public class AliveCompareRequest {
    /**
     * 身份证号
     */
    private String idcard;

    /**
     * 姓名
     */
    private String username;
}