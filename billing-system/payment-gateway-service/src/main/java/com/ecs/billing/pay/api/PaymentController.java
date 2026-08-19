package com.ecs.billing.pay.api;

import com.ecs.billing.pay.PaymentStatusStore;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.payment.spi.BharatQrFactory;
import com.ecs.payment.spi.DynamicBharatQr;
import com.ecs.payment.spi.UpiIntentResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/payments")
public class PaymentController {

    private final PaymentStatusStore statusStore;

    public PaymentController(PaymentStatusStore statusStore) {
        this.statusStore = statusStore;
    }

    public record QrRequest(String orderId, BigDecimal amount, String vpa, String merchantName, String mcc) {}

    @PostMapping("/upi/bharat-qr")
    public ApiResponse<Map<String, Object>> qr(@RequestBody QrRequest request) {
        DynamicBharatQr qr = BharatQrFactory.create(request.vpa(), request.merchantName(), request.mcc(),
                request.orderId(), request.amount());
        UpiIntentResponse intents = BharatQrFactory.intents(qr.upiUri());
        statusStore.put(qr.txnId(), "PENDING");
        return ApiResponse.ok(Map.of(
                "paymentId", UUID.randomUUID().toString(),
                "qr", qr,
                "intents", intents,
                "wsPath", "/ws/payments/" + qr.txnId()
        ));
    }

    @GetMapping("/{txnId}/status")
    public ApiResponse<Map<String, String>> poll(@PathVariable String txnId) {
        return ApiResponse.ok(Map.of("txnId", txnId, "status", statusStore.get(txnId)));
    }

    @PostMapping("/{txnId}/simulate-success")
    public ApiResponse<Map<String, String>> simulate(@PathVariable String txnId) {
        statusStore.put(txnId, "CAPTURED");
        return ApiResponse.ok(Map.of("txnId", txnId, "status", "CAPTURED"));
    }
}
