package com.ecs.payment.spi;

import java.time.Instant;
import java.util.Map;

public record WebhookEvent(
        String provider,
        String signature,
        String rawBody,
        PaymentStatus status,
        String providerTxnId,
        Instant receivedAt,
        Map<String, Object> payload
) {}
