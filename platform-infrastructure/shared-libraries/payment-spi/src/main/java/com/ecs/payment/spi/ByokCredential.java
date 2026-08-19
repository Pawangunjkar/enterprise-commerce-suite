package com.ecs.payment.spi;

public record ByokCredential(
        String provider,
        String keyId,
        String encryptedSecret,
        String merchantId,
        String vpa,
        String mcc
) {}
