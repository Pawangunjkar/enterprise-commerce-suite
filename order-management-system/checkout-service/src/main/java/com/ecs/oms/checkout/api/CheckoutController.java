package com.ecs.oms.checkout.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.common.core.http.DownstreamClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/checkout")
public class CheckoutController {
    private static final Set<String> HIGH_RISK = Set.of("999999", "000000");

    private final DownstreamClient downstreamClient;
    private final String pincodeBaseUrl;

    public CheckoutController(
            DownstreamClient downstreamClient,
            @Value("${ecs.downstream.pincode-url:http://localhost:8091}") String pincodeBaseUrl
    ) {
        this.downstreamClient = downstreamClient;
        this.pincodeBaseUrl = pincodeBaseUrl.endsWith("/") ? pincodeBaseUrl.substring(0, pincodeBaseUrl.length() - 1) : pincodeBaseUrl;
    }

    public record Intent(String cartId, String pincode, String paymentMode, BigDecimal amount, String gstin) {}

    @PostMapping("/intent")
    public ApiResponse<Map<String, Object>> intent(@RequestBody Intent intent) {
        if ("COD".equalsIgnoreCase(intent.paymentMode()) && (intent.amount().compareTo(BigDecimal.valueOf(25000)) > 0
                || HIGH_RISK.contains(intent.pincode()))) {
            throw DomainException.unprocessable("COD_INELIGIBLE", "COD is not available for this cart or pincode");
        }
        Map<?, ?> serviceability = downstreamClient.getUrl(
                pincodeBaseUrl + "/api/v1/pincodes/" + intent.pincode() + "/serviceability",
                Map.class);
        Object serviceable = serviceability.get("serviceable");
        if (Boolean.FALSE.equals(serviceable)) {
            throw DomainException.unprocessable("NOT_SERVICEABLE", "Pincode is not serviceable: " + intent.pincode());
        }
        return ApiResponse.ok(Map.of(
                "checkoutId", UUID.randomUUID().toString(),
                "cartId", intent.cartId(),
                "paymentMode", intent.paymentMode(),
                "gstin", intent.gstin() == null ? "" : intent.gstin(),
                "edd", String.valueOf(serviceability.get("edd")),
                "oda", String.valueOf(serviceability.get("oda"))
        ));
    }
}
