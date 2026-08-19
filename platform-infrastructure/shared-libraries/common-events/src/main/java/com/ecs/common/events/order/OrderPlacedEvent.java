package com.ecs.common.events.order;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

public record OrderPlacedEvent(
        UUID orderId,
        String orderNumber,
        UUID customerId,
        String pincode,
        String originStateCode,
        String destinationStateCode,
        BigDecimal grandTotalInr,
        String paymentMode,
        List<Line> lines
) {
    public record Line(UUID skuId, String sku, int qty, BigDecimal unitPrice, String hsnCode) {}
}
