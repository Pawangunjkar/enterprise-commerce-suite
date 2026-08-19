package com.ecs.billing.pricebook.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/price-books")
public class PriceBookController {
    @GetMapping("/{sku}")
    public ApiResponse<Map<String, Object>> get(@PathVariable String sku) {
        return ApiResponse.ok(Map.of("sku", sku, "mrp", new BigDecimal("79999.00"), "channel", "D2C"));
    }
}
