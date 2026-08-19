package com.ecs.oms.cart.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.Duration;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/carts")
public class CartController {
    private final StringRedisTemplate redis;

    public CartController(StringRedisTemplate redis) { this.redis = redis; }

    public record Line(String sku, int qty, BigDecimal unitPrice) {}

    @PostMapping("/{cartId}/items")
    public ApiResponse<Map<String, String>> add(@PathVariable String cartId, @RequestBody Line line) {
        String key = "cart:" + cartId;
        redis.opsForHash().put(key, line.sku(), line.qty() + ":" + line.unitPrice());
        redis.expire(key, Duration.ofHours(24));
        return ApiResponse.ok(Map.of("cartId", cartId, "sku", line.sku(), "qty", String.valueOf(line.qty())));
    }

    @GetMapping("/{cartId}")
    public ApiResponse<Map<Object, Object>> get(@PathVariable String cartId) {
        return ApiResponse.ok(redis.opsForHash().entries("cart:" + cartId));
    }
}
