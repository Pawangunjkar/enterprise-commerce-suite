package com.ecs.common.events.catalog;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record ProductPublishedEvent(
        UUID productId,
        String sku,
        String name,
        String hsnCode,
        String status,
        Instant effectiveFrom,
        Instant effectiveTo,
        Map<String, Object> attributes,
        BigDecimal listPriceInr,
        String brand,
        String categoryPath
) {}
