package com.ecs.payment.spi;

import java.math.BigDecimal;
import java.util.UUID;

public record CaptureRequest(UUID paymentId, UUID orderId, BigDecimal amountInr, String providerTxnId) {}
