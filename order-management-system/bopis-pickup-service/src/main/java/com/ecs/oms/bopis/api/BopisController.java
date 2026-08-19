package com.ecs.oms.bopis.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/bopis")
public class BopisController {
    @PostMapping("/reservations")
    public ApiResponse<Map<String, String>> reserve(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of("reservationId", UUID.randomUUID().toString(), "hub", body.getOrDefault("hub", "DEL-HUB-01"), "status", "READY_FOR_PICKUP"));
    }
}
