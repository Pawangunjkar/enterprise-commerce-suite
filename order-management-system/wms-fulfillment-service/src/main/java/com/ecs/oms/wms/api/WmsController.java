package com.ecs.oms.wms.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/wms")
public class WmsController {
    public record PickLine(String sku, String bin, int qty) {}

    @PostMapping("/waves")
    public ApiResponse<Map<String, Object>> createWave(@RequestBody List<PickLine> lines) {
        return ApiResponse.ok(Map.of("waveId", UUID.randomUUID().toString(), "lines", lines, "status", "RELEASED"));
    }
}
