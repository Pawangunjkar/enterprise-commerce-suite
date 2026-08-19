package com.ecs.oms.atp.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/inventory")
public class AtpController {
    private final Map<String, Integer> stock = new ConcurrentHashMap<>(Map.of("SKU-PHONE-8-128-BLACK", 42));

    public record LockRequest(String sku, int qty, String warehouse) {}

    @PostMapping("/lock")
    public ApiResponse<Map<String, Integer>> lock(@RequestBody LockRequest request) {
        int available = stock.getOrDefault(request.sku(), 0);
        if (available < request.qty()) {
            throw DomainException.unprocessable("ATP_SHORTAGE", "Only " + available + " units available");
        }
        stock.put(request.sku(), available - request.qty());
        return ApiResponse.ok(Map.of("remaining", stock.get(request.sku())));
    }
}
