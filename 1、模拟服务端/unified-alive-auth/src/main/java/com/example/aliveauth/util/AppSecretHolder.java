package com.example.aliveauth.util;

import lombok.Getter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * 应用密钥持有者
 * 从配置文件中加载appId和appSecret映射
 */
@Getter
@Component
@ConfigurationProperties(prefix = "app")
public class AppSecretHolder {

    /**
     * appId -> appSecret 映射
     */
    private Map<String, String> appSecrets;

    /**
     * 应用信息列表 (用于配置绑定)
     */
    private List<AppInfo> apps;

    public void setApps(List<AppInfo> apps) {
        this.apps = apps;
        this.appSecrets = apps.stream()
                .collect(Collectors.toMap(AppInfo::getAppId, AppInfo::getAppSecret));
    }

    /**
     * 根据appId获取appSecret
     */
    public Optional<String> getSecret(String appId) {
        return Optional.ofNullable(appSecrets.get(appId));
    }

    /**
     * 应用信息内部类
     */
    @Getter
    public static class AppInfo {
        private String appId;
        private String appSecret;
        private String appName;

        public void setAppId(String appId) {
            this.appId = appId;
        }

        public void setAppSecret(String appSecret) {
            this.appSecret = appSecret;
        }

        public void setAppName(String appName) {
            this.appName = appName;
        }
    }
}