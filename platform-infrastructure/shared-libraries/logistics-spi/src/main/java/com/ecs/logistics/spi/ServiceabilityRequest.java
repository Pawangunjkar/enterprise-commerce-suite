package com.ecs.logistics.spi;

import java.math.BigDecimal;

public record ServiceabilityRequest(
        String originPincode,
        String destinationPincode,
        BigDecimal weightKg,
        BigDecimal declaredValueInr,
        boolean cod
) {}
