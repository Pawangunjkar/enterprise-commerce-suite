package com.ecs.billing.cod.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/cod")
public class CodReconcileController {
    public record Match(String awb, BigDecimal carrierAmount, BigDecimal bankAmount) {}
    @PostMapping("/match")
    public ApiResponse<Map<String, Object>> match(@RequestBody Match request) {
        boolean ok = request.carrierAmount().compareTo(request.bankAmount()) == 0;
        return ApiResponse.ok(Map.of("awb", request.awb(), "matched", ok, "delta", request.carrierAmount().subtract(request.bankAmount())));
    }
}
