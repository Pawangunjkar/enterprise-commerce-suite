package com.ecs.mec.bundle.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@RestController
@RequestMapping("/api/v1/catalog/bundles")
public class BomController {
    public record Component(String sku, int qty, BigDecimal unitPrice) {}
    public record Bom(String bundleSku, List<Component> components, BigDecimal bundleDiscountPct) {}

    @PostMapping("/price")
    public ApiResponse<BigDecimal> price(@RequestBody Bom bom) {
        BigDecimal sum = bom.components().stream()
                .map(c -> c.unitPrice().multiply(BigDecimal.valueOf(c.qty())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal discount = sum.multiply(bom.bundleDiscountPct()).divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
        return ApiResponse.ok(sum.subtract(discount));
    }
}
