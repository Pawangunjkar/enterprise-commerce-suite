package com.ecs.common.events.logistics;

import java.util.UUID;

public record ShipmentEvent(
        UUID shipmentId,
        UUID orderId,
        String carrier,
        String awb,
        String status,
        String originPincode,
        String destinationPincode
) {}
