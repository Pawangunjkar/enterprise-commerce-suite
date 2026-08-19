package com.ecs.common.events;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;
import java.util.UUID;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CloudEventEnvelope<T>(
        String specversion,
        String type,
        String source,
        String id,
        Instant time,
        String datacontenttype,
        String subject,
        String tenantId,
        T data
) {
    public static <T> CloudEventEnvelope<T> of(String type, String source, String tenantId, String subject, T data) {
        return new CloudEventEnvelope<>(
                "1.0",
                type,
                source,
                UUID.randomUUID().toString(),
                Instant.now(),
                "application/json",
                subject,
                tenantId,
                data
        );
    }
}
