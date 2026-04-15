package com.example.aliveauth.service.impl;

import cn.hutool.core.util.IdUtil;
import com.example.aliveauth.dto.response.TokenResponse;
import com.example.aliveauth.service.TokenService;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Token服务实现类
 * 使用内存存储Token信息
 */
@Service
public class TokenServiceImpl implements TokenService {

    /**
     * Token有效期: 2小时 = 7200秒
     */
    private static final long TOKEN_EXPIRE_SECONDS = 7200L;

    /**
     * Token存储: token -> TokenInfo
     */
    private final Map<String, TokenInfo> tokenStore = new ConcurrentHashMap<>();

    @Override
    public TokenResponse generateToken(String appId) {
        // 生成唯一Token
        String token = IdUtil.fastSimpleUUID();
        long createTime = System.currentTimeMillis();
        long expireTime = createTime + (TOKEN_EXPIRE_SECONDS * 1000);

        // 存储Token信息
        TokenInfo tokenInfo = new TokenInfo(appId, createTime, expireTime);
        tokenStore.put(token, tokenInfo);

        // 构建响应
        TokenResponse response = new TokenResponse();
        response.setToken(token);
        response.setExpiresIn(TOKEN_EXPIRE_SECONDS);
        response.setCreateTime(createTime);

        return response;
    }

    @Override
    public boolean validateToken(String token) {
        if (token == null || token.isEmpty()) {
            return false;
        }

        TokenInfo tokenInfo = tokenStore.get(token);
        if (tokenInfo == null) {
            return false;
        }

        // 检查是否过期
        if (System.currentTimeMillis() > tokenInfo.getExpireTime()) {
            tokenStore.remove(token);
            return false;
        }

        return true;
    }

    @Override
    public Optional<String> getAppIdByToken(String token) {
        if (token == null || token.isEmpty()) {
            return Optional.empty();
        }

        TokenInfo tokenInfo = tokenStore.get(token);
        if (tokenInfo != null && System.currentTimeMillis() <= tokenInfo.getExpireTime()) {
            return Optional.of(tokenInfo.getAppId());
        }

        return Optional.empty();
    }

    /**
     * Token信息内部类 (Java 8兼容)
     */
    private static class TokenInfo {
        private final String appId;
        private final long createTime;
        private final long expireTime;

        public TokenInfo(String appId, long createTime, long expireTime) {
            this.appId = appId;
            this.createTime = createTime;
            this.expireTime = expireTime;
        }

        public String getAppId() { return appId; }
        public long getCreateTime() { return createTime; }
        public long getExpireTime() { return expireTime; }
    }
}