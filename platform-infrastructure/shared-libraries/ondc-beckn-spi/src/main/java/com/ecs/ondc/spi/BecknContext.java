package com.ecs.ondc.spi;

public record BecknContext(
        String domain,
        String country,
        String city,
        String action,
        String coreVersion,
        String bapId,
        String bapUri,
        String bppId,
        String bppUri,
        String transactionId,
        String messageId,
        String timestamp
) {}
