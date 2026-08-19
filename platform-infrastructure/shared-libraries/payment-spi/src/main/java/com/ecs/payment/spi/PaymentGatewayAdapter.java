package com.ecs.payment.spi;

public interface PaymentGatewayAdapter {
    String providerId();

    AuthorizeResponse authorize(AuthorizeRequest request, ByokCredential credential);

    PaymentStatus capture(CaptureRequest request, ByokCredential credential);

    PaymentStatus refund(String providerTxnId, java.math.BigDecimal amountInr, ByokCredential credential);

    boolean verifyWebhook(WebhookEvent event, ByokCredential credential);
}
