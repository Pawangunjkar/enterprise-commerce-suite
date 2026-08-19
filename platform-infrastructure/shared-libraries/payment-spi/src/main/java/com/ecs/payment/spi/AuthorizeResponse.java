package com.ecs.payment.spi;

import java.util.UUID;

public record AuthorizeResponse(
        UUID paymentId,
        PaymentStatus status,
        String provider,
        String providerTxnId,
        String redirectUrl,
        UpiIntentResponse upiIntent,
        DynamicBharatQr bharatQr
) {}
