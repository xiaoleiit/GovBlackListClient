package com.example.aliveauth.dto.response;

import lombok.Data;

/**
 * 生存比对响应内容 (加密前)
 */
@Data
public class AliveCompareResponse {
    /**
     * 身份证号
     */
    private String idcard;

    /**
     * 姓名
     */
    private String username;

    /**
     * 比对结果: 1-一致, 0-不一致
     */
    private Integer compareResult;

    /**
     * 比对说明
     */
    private String compareMsg;

    /**
     * 生存状态: ALIVE-存活, DEAD-已故, UNKNOWN-未知
     */
    private String aliveStatus;
}