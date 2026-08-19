package com.ecs.billing.emi.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/emi")
public class EmiController {
    @GetMapping("/quote")
    public ApiResponse<Map<String, Object>> quote(@RequestParam BigDecimal principal, @RequestParam int months) {
        BigDecimal installment = principal.divide(BigDecimal.valueOf(months), 2, RoundingMode.HALF_UP);
        return ApiResponse.ok(Map.of("principal", principal, "months", months, "installment", installment, "noCost", true));
    }
}
