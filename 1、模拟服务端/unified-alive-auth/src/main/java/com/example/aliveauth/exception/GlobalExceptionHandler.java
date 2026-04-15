package com.example.aliveauth.exception;

import com.example.aliveauth.dto.response.OpenApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理器
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理认证异常
     */
    @ExceptionHandler(AuthException.class)
    @ResponseStatus(HttpStatus.OK)
    public OpenApiResponse handleAuthException(AuthException e) {
        log.error("认证异常: {}", e.getMessage(), e);
        return OpenApiResponse.fail(e.getErrorCode().getCode(), e.getMessage());
    }

    /**
     * 处理参数校验异常
     */
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.OK)
    public OpenApiResponse handleIllegalArgumentException(IllegalArgumentException e) {
        log.error("参数异常: {}", e.getMessage(), e);
        return OpenApiResponse.fail(ErrorCode.PARAM_ERROR.getCode(), e.getMessage());
    }

    /**
     * 处理其他异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public OpenApiResponse handleException(Exception e) {
        log.error("系统异常: {}", e.getMessage(), e);
        return OpenApiResponse.fail(ErrorCode.SYSTEM_ERROR.getCode(), "系统错误");
    }
}