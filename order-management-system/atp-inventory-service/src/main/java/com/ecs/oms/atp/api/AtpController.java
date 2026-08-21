package com.ecs.oms.atp.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/inventory")
public class AtpController {
    private final Map<String, Integer> stock = new ConcurrentHashMap<>(Map.of(
            "SKU-PHONE-8-128-BLACK", 42,
            "SKU-PHONE-12-256-GOLD", 18,
            "SKU-BUDS-PRO", 80,
            "SKU-CHARGER-65W", 120
    ));

    public record LockRequest(String sku, int qty, String warehouse) {}

    public record UnlockRequest(String sku, int qty) {}

    @PostMapping("/lock")
    public ApiResponse<Map<String, Integer>> lock(@RequestBody LockRequest request) {
        int available = stock.computeIfAbsent(request.sku(), key -> 100);
        if (available < request.qty()) {
            throw DomainException.unprocessable("ATP_SHORTAGE", "Only " + available + " units available");
        }
        stock.put(request.sku(), available - request.qty());
        return ApiResponse.ok(Map.of("remaining", stock.get(request.sku())));
    }

    @PostMapping("/unlock")
    public ApiResponse<Map<String, Integer>> unlock(@RequestBody UnlockRequest request) {
        int remaining = stock.merge(request.sku(), request.qty(), Integer::sum);
        return ApiResponse.ok(Map.of("remaining", remaining));
    }
}
