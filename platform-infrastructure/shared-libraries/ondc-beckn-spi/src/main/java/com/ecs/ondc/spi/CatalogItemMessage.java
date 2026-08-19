package com.ecs.ondc.spi;

import java.math.BigDecimal;

public record CatalogItemMessage(
        String id,
        String descriptor,
        String categoryId,
        BigDecimal priceInr,
        int availableQty,
        String fulfillmentId
) {}
