package com.ecs.ondc.spi;

import java.math.BigDecimal;
import java.util.List;

public record OrderMessage(
        String id,
        String status,
        BigDecimal totalInr,
        List<CatalogItemMessage> items
) {}
