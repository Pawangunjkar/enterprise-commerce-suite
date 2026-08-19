package com.ecs.billing.plugins;

import com.ecs.payment.spi.AuthorizeRequest;
import com.ecs.payment.spi.AuthorizeResponse;
import com.ecs.payment.spi.BharatQrFactory;
import com.ecs.payment.spi.ByokCredential;
import com.ecs.payment.spi.CaptureRequest;
import com.ecs.payment.spi.DynamicBharatQr;
import com.ecs.payment.spi.PaymentGatewayAdapter;
import com.ecs.payment.spi.PaymentStatus;
import com.ecs.payment.spi.WebhookEvent;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;
import java.util.UUID;

@Component
public class PhonePeAdapter implements PaymentGatewayAdapter {

    @Override
    public String providerId() {
        return "PHONEPE";
    }

    @Override
    public AuthorizeResponse authorize(AuthorizeRequest request, ByokCredential credential) {
        DynamicBharatQr qr = BharatQrFactory.create(credential.vpa(), "ECS Merchant", credential.mcc(),
                request.orderNumber(), request.amountInr());
        return new AuthorizeResponse(UUID.randomUUID(), PaymentStatus.PENDING, providerId(),
                "ppe_" + UUID.randomUUID().toString().substring(0, 8),
                "phonepe://pay?am=" + request.amountInr(),
                BharatQrFactory.intents(qr.upiUri()), qr);
    }

    @Override
    public PaymentStatus capture(CaptureRequest request, ByokCredential credential) {
        return PaymentStatus.CAPTURED;
    }

    @Override
    public PaymentStatus refund(String providerTxnId, java.math.BigDecimal amountInr, ByokCredential credential) {
        return PaymentStatus.REFUNDED;
    }

    @Override
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
