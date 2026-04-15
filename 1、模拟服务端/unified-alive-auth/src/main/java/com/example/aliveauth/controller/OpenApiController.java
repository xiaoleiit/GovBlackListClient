package com.example.aliveauth.controller;

import cn.hutool.json.JSONUtil;
import com.example.aliveauth.dto.request.AliveCompareRequest;
import com.example.aliveauth.dto.request.OpenApiRequest;
import com.example.aliveauth.dto.request.TokenRequest;
import com.example.aliveauth.dto.response.AliveCompareResponse;
import com.example.aliveauth.dto.response.OpenApiResponse;
import com.example.aliveauth.dto.response.TokenResponse;
import com.example.aliveauth.exception.AuthException;
import com.example.aliveauth.exception.ErrorCode;
import com.example.aliveauth.security.CryptoService;
import com.example.aliveauth.service.AliveCompareService;
import com.example.aliveauth.service.TokenService;
import com.example.aliveauth.util.AppSecretHolder;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 统一接口控制器
 * 实现5.1生成Token接口和5.4生存比对接口
 */
@Slf4j
@RestController
@RequestMapping("/openapi")
@RequiredArgsConstructor
public class OpenApiController {

    private final CryptoService cryptoService;
    private final TokenService tokenService;
    private final AliveCompareService aliveCompareService;
    private final AppSecretHolder appSecretHolder;

    /**
     * 5.1 生成Token接口
     * 此接口不需要Token验证
     *
     * @param request 统一请求报文
     * @return 统一响应报文
     */
    @PostMapping("/stoken")
    public OpenApiResponse generateToken(@Valid @RequestBody OpenApiRequest request) {
        log.info("收到生成Token请求, appId: {}", request.getAppId());

        // 1. 获取应用密钥
        String appSecret = appSecretHolder.getSecret(request.getAppId())
                .orElseThrow(() -> new AuthException(ErrorCode.APP_NOT_FOUND, "应用不存在"));

        // 2. 验证签名
        if (!cryptoService.verifySM3Sign(appSecret, request.getEncryptData(), request.getSign())) {
            throw new AuthException(ErrorCode.SIGN_INVALID, "签名验证失败");
        }

        // 3. 解密请求内容
        String decryptedData = cryptoService.decryptBySM4(request.getEncryptData(), appSecret);
        TokenRequest tokenRequest = JSONUtil.toBean(decryptedData, TokenRequest.class);

        // 4. 验证appId和appSecret匹配
        if (!request.getAppId().equals(tokenRequest.getAppId())
                || !appSecret.equals(tokenRequest.getAppSecret())) {
            throw new AuthException(ErrorCode.AUTH_FAILED, "应用ID或密钥不匹配");
        }

        // 5. 生成Token
        TokenResponse tokenResponse = tokenService.generateToken(request.getAppId());

        // 6. 加密响应并签名
        String responseData = JSONUtil.toJsonStr(tokenResponse);
        String encryptData = cryptoService.encryptBySM4(responseData, appSecret);
        String sign = cryptoService.signBySM3(appSecret, encryptData);

        log.info("Token生成成功, appId: {}, token: {}", request.getAppId(), tokenResponse.getToken());
        return OpenApiResponse.success(request.getAppId(), encryptData, sign);
    }

    /**
     * 5.4 生存比对接口
     * 需要Token验证(通过拦截器实现)
     *
     * @param request    统一请求报文
     * @param httpRequest HTTP请求(用于获取appId)
     * @return 统一响应报文
     */
    @PostMapping("/aliveCompare")
    public OpenApiResponse aliveCompare(
            @Valid @RequestBody OpenApiRequest request,
            HttpServletRequest httpRequest) {

        // 从请求属性获取appId(由Token拦截器设置)
        String appId = (String) httpRequest.getAttribute("appId");
        log.info("收到生存比对请求, appId: {}", appId);

        // 1. 获取应用密钥
        String appSecret = appSecretHolder.getSecret(appId)
                .orElseThrow(() -> new AuthException(ErrorCode.APP_NOT_FOUND, "应用不存在"));

        // 2. 验证签名
        if (!cryptoService.verifySM3Sign(appSecret, request.getEncryptData(), request.getSign())) {
            throw new AuthException(ErrorCode.SIGN_INVALID, "签名验证失败");
        }

        // 3. 解密请求内容
        String decryptedData = cryptoService.decryptBySM4(request.getEncryptData(), appSecret);
        List<AliveCompareRequest> compareRequests = JSONUtil.toList(decryptedData, AliveCompareRequest.class);

        // 4. 执行生存比对
        List<AliveCompareResponse> compareResponses = aliveCompareService.compare(compareRequests);

        // 5. 加密响应并签名
        String responseData = JSONUtil.toJsonStr(compareResponses);
        String encryptData = cryptoService.encryptBySM4(responseData, appSecret);
        String sign = cryptoService.signBySM3(appSecret, encryptData);

        log.info("生存比对完成, appId: {}, 比对数量: {}", appId, compareRequests.size());
        return OpenApiResponse.success(appId, encryptData, sign);
    }
}