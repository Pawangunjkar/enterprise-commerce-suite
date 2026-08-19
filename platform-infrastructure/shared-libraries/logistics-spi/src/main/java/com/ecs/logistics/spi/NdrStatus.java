package com.ecs.logistics.spi;

import java.time.Instant;

public record NdrStatus(
        String awb,
        String reasonCode,
        String reasonText,
        int attemptCount,
        Instant lastAttemptAt,
        boolean rtoInitiated
) {}
