package com.ecs.logistics.spi;

import java.math.BigDecimal;
import java.time.LocalDate;

public record ServiceabilityResponse(
        boolean serviceable,
        boolean oda,
        BigDecimal shippingChargeInr,
        int transitDays,
        LocalDate estimatedDeliveryDate,
        String zone
) {}
