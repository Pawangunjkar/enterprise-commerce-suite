package com.ecs.billing.tcs.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/tcs")
public class TcsController {
    @PostMapping("/194o")
    public ApiResponse<Map<String, Object>> section194O(@RequestBody Map<String, BigDecimal> body) {
        BigDecimal gmv = body.getOrDefault("gmv", BigDecimal.ZERO);
        BigDecimal tcs = gmv.multiply(new BigDecimal("0.01")).setScale(2, RoundingMode.HALF_UP);
        return ApiResponse.ok(Map.of("section", "194O", "gmv", gmv, "tcs", tcs));
    }
}
