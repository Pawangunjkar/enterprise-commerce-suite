package com.ecs.payment.spi;

public record UpiIntentResponse(
        String gpay,
        String phonepe,
        String paytm,
        String cred,
        String generic
) {}
