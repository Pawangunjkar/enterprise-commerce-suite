package com.ecs.oms.price.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.events.Topics;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/prices")
public class PriceController {
    private final StringRedisTemplate redis;
    public PriceController(StringRedisTemplate redis) { this.redis = redis; }

    public record CalcRequest(String sku, BigDecimal basePrice, BigDecimal offerDiscount, BigDecimal loyaltyDiscount) {}

    @PostMapping("/calculate")
    public ApiResponse<Map<String, Object>> calculate(@RequestBody CalcRequest request) {
        String cached = redis.opsForValue().get("price:" + request.sku());
        BigDecimal offer = request.offerDiscount() == null ? BigDecimal.ZERO : request.offerDiscount();
        BigDecimal loyalty = request.loyaltyDiscount() == null ? BigDecimal.ZERO : request.loyaltyDiscount();
        BigDecimal effective = request.basePrice().subtract(offer).subtract(loyalty).max(BigDecimal.ZERO)
                .setScale(2, RoundingMode.HALF_UP);
        redis.opsForValue().set("price:" + request.sku(), effective.toPlainString());
        return ApiResponse.ok(Map.of("sku", request.sku(), "effectivePrice", effective, "cached", cached != null));
    }

    @KafkaListener(topics = Topics.CATALOG_OFFER_ACTIVATED)
    public void onOffer(String payload) {
        redis.keys("price:*").forEach(redis::delete);
    }

    @Scheduled(cron = "0 5 0 * * *", zone = "Asia/Kolkata")
    public void eod() {
        redis.keys("price:*").forEach(redis::delete);
    }
}
