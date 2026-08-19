package com.ecs.oms.checkout.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/checkout")
public class CheckoutController {
    private static final Set<String> HIGH_RISK = Set.of("999999", "000000");

    public record Intent(String cartId, String pincode, String paymentMode, BigDecimal amount, String gstin) {}

    @PostMapping("/intent")
    public ApiResponse<Map<String, Object>> intent(@RequestBody Intent intent) {
        if ("COD".equalsIgnoreCase(intent.paymentMode()) && (intent.amount().compareTo(BigDecimal.valueOf(25000)) > 0
                || HIGH_RISK.contains(intent.pincode()))) {
            throw DomainException.unprocessable("COD_INELIGIBLE", "COD is not available for this cart or pincode");
        }
        return ApiResponse.ok(Map.of(
                "checkoutId", UUID.randomUUID().toString(),
                "cartId", intent.cartId(),
                "paymentMode", intent.paymentMode(),
                "gstin", intent.gstin() == null ? "" : intent.gstin()
        ));
    }
}
