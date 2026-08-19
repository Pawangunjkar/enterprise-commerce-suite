package com.ecs.common.events.billing;

import java.math.BigDecimal;
import java.util.UUID;

public record PaymentEvent(
        UUID paymentId,
        UUID orderId,
        String provider,
        String method,
        String status,
        BigDecimal amountInr,
        String upiVpa,
        String providerTxnId
) {}
