package com.example.aliveauth.service;

import com.example.aliveauth.dto.request.AliveCompareRequest;
import com.example.aliveauth.dto.response.AliveCompareResponse;

import java.util.List;

/**
 * 生存比对服务接口
 */
public interface AliveCompareService {

    /**
     * 执行生存比对
     *
     * @param requests 比对请求列表
     * @return 比对结果列表
     */
    List<AliveCompareResponse> compare(List<AliveCompareRequest> requests);
}