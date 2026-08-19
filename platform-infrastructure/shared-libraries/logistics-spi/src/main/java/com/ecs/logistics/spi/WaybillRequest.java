package com.ecs.logistics.spi;

import java.math.BigDecimal;
import java.util.UUID;

public record WaybillRequest(
        UUID orderId,
        String consigneeName,
        String consigneeMobile,
        String destinationPincode,
        String destinationAddress,
        BigDecimal weightKg,
        BigDecimal collectableInr,
        boolean cod
) {}
