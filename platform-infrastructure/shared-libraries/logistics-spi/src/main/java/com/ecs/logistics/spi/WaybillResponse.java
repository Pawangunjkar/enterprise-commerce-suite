package com.ecs.logistics.spi;

public record WaybillResponse(
        String carrier,
        String awb,
        String labelPdfBase64,
        String trackingUrl
) {}
