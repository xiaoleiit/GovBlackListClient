package com.example.aliveauth.service;

import com.example.aliveauth.dto.response.TokenResponse;

import java.util.Optional;

/**
 * Token服务接口
 */
public interface TokenService {

    /**
     * 生成Token
     *
     * @param appId 应用ID
     * @return Token响应
     */
    TokenResponse generateToken(String appId);

    /**
     * 验证Token是否有效
     *
     * @param token 待验证的Token
     * @return 是否有效
     */
    boolean validateToken(String token);

    /**
     * 根据Token获取AppId
     *
     * @param token Token值
     * @return AppId (如果Token有效)
     */
    Optional<String> getAppIdByToken(String token);
}