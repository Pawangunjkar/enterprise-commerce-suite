package com.ecs.common.events.catalog;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public record OfferActivatedEvent(
        UUID offerId,
        String offerCode,
        String offerType,
        BigDecimal discountValue,
        String discountKind,
        Instant validFrom,
        Instant validTo,
        UUID productId,
        String sku
) {}
