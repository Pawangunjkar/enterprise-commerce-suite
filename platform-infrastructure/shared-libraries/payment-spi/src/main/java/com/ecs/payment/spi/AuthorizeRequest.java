package com.ecs.payment.spi;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

public record AuthorizeRequest(
        UUID orderId,
        String orderNumber,
        BigDecimal amountInr,
        PaymentMethod method,
        String customerMobile,
        String returnUrl,
        Map<String, String> metadata
) {}
