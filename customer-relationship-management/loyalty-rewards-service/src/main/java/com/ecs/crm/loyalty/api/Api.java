package com.ecs.crm.loyalty.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/loyalty")
public class Api {
    @GetMapping("/{customerId}")
    public ApiResponse<Map<String, Object>> get(@PathVariable String customerId, @RequestParam(defaultValue = "1.0") double festivalMultiplier) {
        return ApiResponse.ok(Map.of("customerId", customerId, "tier", "GOLD", "points", 4200, "festivalMultiplier", festivalMultiplier,
                "redeemableInr", new BigDecimal("420.00")));
    }
}
