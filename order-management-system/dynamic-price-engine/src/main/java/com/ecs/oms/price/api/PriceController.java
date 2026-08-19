package com.ecs.oms.price.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.cache.EcsCacheConfiguration;
import com.ecs.common.events.Topics;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.Cursor;
import org.springframework.data.redis.core.ScanOptions;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/prices")
public class PriceController {
    private final StringRedisTemplate redis;

    public PriceController(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public record CalcRequest(String sku, BigDecimal basePrice, BigDecimal offerDiscount, BigDecimal loyaltyDiscount) {}

    @PostMapping("/calculate")
    @Cacheable(cacheNames = EcsCacheConfiguration.PRICES, key = "#request.sku + ':' + #request.basePrice + ':' + #request.offerDiscount + ':' + #request.loyaltyDiscount")
    public ApiResponse<Map<String, Object>> calculate(@RequestBody CalcRequest request) {
        BigDecimal offer = request.offerDiscount() == null ? BigDecimal.ZERO : request.offerDiscount();
        BigDecimal loyalty = request.loyaltyDiscount() == null ? BigDecimal.ZERO : request.loyaltyDiscount();
        BigDecimal effective = request.basePrice().subtract(offer).subtract(loyalty).max(BigDecimal.ZERO)
                .setScale(2, RoundingMode.HALF_UP);
        redis.opsForValue().set("price:" + request.sku(), effective.toPlainString());
        return ApiResponse.ok(Map.of("sku", request.sku(), "effectivePrice", effective));
    }

    @KafkaListener(topics = Topics.CATALOG_OFFER_ACTIVATED)
    @CacheEvict(cacheNames = EcsCacheConfiguration.PRICES, allEntries = true)
    public void onOffer(String payload) {
        evictRedisPrices();
    }

    @Scheduled(cron = "0 5 0 * * *", zone = "Asia/Kolkata")
    @CacheEvict(cacheNames = EcsCacheConfiguration.PRICES, allEntries = true)
    public void eod() {
        evictRedisPrices();
    }

    private void evictRedisPrices() {
        ScanOptions options = ScanOptions.scanOptions().match("price:*").count(200).build();
        try (Cursor<String> cursor = redis.scan(options)) {
            cursor.forEachRemaining(redis::delete);
        }
    }
}
