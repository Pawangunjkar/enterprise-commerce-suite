package com.ecs.billing.plugins;

import com.ecs.payment.spi.*;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;
import java.util.UUID;

@Component
public class RazorpayAdapter implements PaymentGatewayAdapter {
    public String providerId() { return "RAZORPAY"; }

    public AuthorizeResponse authorize(AuthorizeRequest request, ByokCredential credential) {
        DynamicBharatQr qr = BharatQrFactory.create(credential.vpa(), "ECS Merchant", credential.mcc(),
                request.orderNumber(), request.amountInr());
        return new AuthorizeResponse(UUID.randomUUID(), PaymentStatus.PENDING, providerId(),
                "rzp_" + UUID.randomUUID().toString().substring(0, 8), null,
                BharatQrFactory.intents(qr.upiUri()), qr);
    }

    public PaymentStatus capture(CaptureRequest request, ByokCredential credential) { return PaymentStatus.CAPTURED; }
    public PaymentStatus refund(String providerTxnId, java.math.BigDecimal amountInr, ByokCredential credential) { return PaymentStatus.REFUNDED; }

    public boolean verifyWebhook(WebhookEvent event, ByokCredential credential) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(credential.encryptedSecret().getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            String expected = HexFormat.of().formatHex(mac.doFinal(event.rawBody().getBytes(StandardCharsets.UTF_8)));
            return expected.equalsIgnoreCase(event.signature());
        } catch (Exception ex) {
            return false;
        }
    }
}
