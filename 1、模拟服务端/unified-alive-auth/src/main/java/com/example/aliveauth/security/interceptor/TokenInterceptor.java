package com.example.aliveauth.security.interceptor;

import com.example.aliveauth.exception.AuthException;
import com.example.aliveauth.exception.ErrorCode;
import com.example.aliveauth.service.TokenService;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * Token验证拦截器
 * 用于拦截需要Token验证的接口
 */
@Component
@RequiredArgsConstructor
public class TokenInterceptor implements HandlerInterceptor {

    private final TokenService tokenService;

    /**
     * Token请求头名称
     */
    private static final String TOKEN_HEADER = "token";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws Exception {

        // 从请求头获取Token
        String token = request.getHeader(TOKEN_HEADER);

        // 验证Token
        if (!tokenService.validateToken(token)) {
            throw new AuthException(ErrorCode.TOKEN_INVALID, "Token无效或已过期");
        }

        // 将appId存入request属性供后续使用
        tokenService.getAppIdByToken(token)
                .ifPresent(appId -> request.setAttribute("appId", appId));

        return true;
    }
}