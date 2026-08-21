package com.ecs.oms.wms.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/wms")
public class WmsController {
    private final Map<String, String> waves = new ConcurrentHashMap<>();

    public record PickLine(String sku, String bin, int qty) {}

    @PostMapping("/waves")
    public ApiResponse<Map<String, Object>> createWave(@RequestBody List<PickLine> lines) {
        String waveId = UUID.randomUUID().toString();
        waves.put(waveId, "RELEASED");
        return ApiResponse.ok(Map.of("waveId", waveId, "lines", lines, "status", "RELEASED"));
    }

    @PostMapping("/waves/{waveId}/cancel")
    public ApiResponse<Map<String, String>> cancel(@PathVariable String waveId) {
        if (!waves.containsKey(waveId)) {
            throw DomainException.notFound("wave", waveId);
        }
        waves.put(waveId, "CANCELLED");
        return ApiResponse.ok(Map.of("waveId", waveId, "status", "CANCELLED"));
    }
}
