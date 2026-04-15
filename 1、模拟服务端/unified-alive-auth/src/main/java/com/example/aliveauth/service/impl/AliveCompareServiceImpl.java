package com.example.aliveauth.service.impl;

import com.example.aliveauth.dto.request.AliveCompareRequest;
import com.example.aliveauth.dto.response.AliveCompareResponse;
import com.example.aliveauth.service.AliveCompareService;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 生存比对服务实现类
 * 使用模拟数据进行比对
 */
@Service
public class AliveCompareServiceImpl implements AliveCompareService {

    /**
     * 模拟人员数据库: 身份证号 -> 人员信息
     */
    private static final Map<String, MockPerson> MOCK_DATABASE = new ConcurrentHashMap<>();

    static {
        // 初始化模拟数据
        MOCK_DATABASE.put("110101199001011234", new MockPerson("张三", true));   // 存活
        MOCK_DATABASE.put("110101198505052345", new MockPerson("李四", false));  // 已故
        MOCK_DATABASE.put("310101199203033456", new MockPerson("王五", true));   // 存活
        MOCK_DATABASE.put("220211200901030983", new MockPerson("奥巴马", true)); // 存活
        MOCK_DATABASE.put("110101196208252029", new MockPerson("陈十四", false));  // 已故
    }

    @Override
    public List<AliveCompareResponse> compare(List<AliveCompareRequest> requests) {
        return requests.stream()
                .map(this::doCompare)
                .collect(Collectors.toList());
    }

    /**
     * 执行单个比对
     */
    private AliveCompareResponse doCompare(AliveCompareRequest request) {
        AliveCompareResponse response = new AliveCompareResponse();
        response.setIdcard(request.getIdcard());
        response.setUsername(request.getUsername());

        MockPerson person = MOCK_DATABASE.get(request.getIdcard());

        if (person == null) {
            // 未找到该人员
            response.setCompareResult(0);
            response.setCompareMsg("未找到该人员信息");
            response.setAliveStatus("UNKNOWN");
        } else {
            // 比对姓名
            boolean nameMatch = person.getName().equals(request.getUsername());
            response.setCompareResult(nameMatch ? 1 : 0);
            response.setCompareMsg(nameMatch ? "比对一致" : "姓名不匹配");
            response.setAliveStatus(person.isAlive() ? "ALIVE" : "DEAD");
        }

        return response;
    }

    /**
     * 模拟人员信息内部类 (Java 8兼容)
     */
    private static class MockPerson {
        private final String name;
        private final boolean alive;

        public MockPerson(String name, boolean alive) {
            this.name = name;
            this.alive = alive;
        }

        public String getName() { return name; }
        public boolean isAlive() { return alive; }
    }
}