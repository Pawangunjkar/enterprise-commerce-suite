package com.ecs.payment.spi;

public record DynamicBharatQr(
        String upiUri,
        String pngBase64,
        String txnId,
        String vpa
) {}
