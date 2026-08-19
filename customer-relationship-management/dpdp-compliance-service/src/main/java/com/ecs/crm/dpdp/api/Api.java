package com.ecs.crm.dpdp.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/dpdp")
public class Api {
    @PostMapping("/consent")
    public ApiResponse<Map<String, Object>> consent(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of("principal", body.get("mobile"), "purpose", body.get("purpose"),
                "grantedAt", Instant.now().toString(), "law", "DPDP Act 2023"));
    }
    @PostMapping("/anonymize/{customerId}")
    public ApiResponse<Map<String, String>> anonymize(@PathVariable String customerId) {
        return ApiResponse.ok(Map.of("customerId", customerId, "status", "ANONYMIZED"));
    }
}
