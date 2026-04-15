package com.example.aliveauth.exception;

import lombok.Getter;

/**
 * 错误码枚举
 */
@Getter
public enum ErrorCode {
    /**
     * 操作成功
     */
    SUCCESS(0, "操作成功"),

    /**
     * 签名验证失败
     */
    SIGN_INVALID(1001, "签名验证失败"),

    /**
     * Token无效或已过期
     */
    TOKEN_INVALID(1002, "Token无效或已过期"),

    /**
     * 应用不存在
     */
    APP_NOT_FOUND(1003, "应用不存在"),

    /**
     * 认证失败
     */
    AUTH_FAILED(1004, "认证失败"),

    /**
     * 解密失败
     */
    DECRYPT_FAILED(1005, "解密失败"),

    /**
     * 参数错误
     */
    PARAM_ERROR(1006, "参数错误"),

    /**
     * 系统错误
     */
    SYSTEM_ERROR(9999, "系统错误");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}