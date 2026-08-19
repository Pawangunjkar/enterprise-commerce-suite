package com.ecs.oms.ndr.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ndr")
public class NdrController {
    @PostMapping("/{awb}/action")
    public ApiResponse<Map<String, String>> action(@PathVariable String awb, @RequestParam String action) {
        String status = "REATTEMPT".equalsIgnoreCase(action) ? "REATTEMPT_SCHEDULED" : "RTO_INITIATED";
        return ApiResponse.ok(Map.of("awb", awb, "status", status));
    }
}
