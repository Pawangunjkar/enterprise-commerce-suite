package com.ecs.billing.pay.api;

import com.ecs.billing.pay.PaymentStatusStore;
import com.ecs.billing.pay.domain.PaymentTxn;
import com.ecs.billing.pay.repo.PaymentTxnRepository;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
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
    private final PaymentTxnRepository payments;

    public PaymentController(PaymentStatusStore statusStore, PaymentTxnRepository payments) {
        this.statusStore = statusStore;
        this.payments = payments;
    }

    public record QrRequest(String orderId, BigDecimal amount, String vpa, String merchantName, String mcc) {}

    public record AuthorizeRequest(String orderId, BigDecimal amount, String mode) {}

    @PostMapping("/authorize")
    public ApiResponse<Map<String, String>> authorize(@RequestBody AuthorizeRequest request) {
        PaymentTxn txn = new PaymentTxn();
        txn.setOrderId(UUID.fromString(request.orderId()));
        txn.setAmountInr(request.amount());
        txn.setMode(request.mode() == null ? "UPI" : request.mode());
        txn.setStatus("AUTHORIZED");
        txn.setTxnRef("AUTH-" + System.currentTimeMillis());
        payments.save(txn);
        statusStore.put(txn.getId().toString(), "AUTHORIZED");
        return ApiResponse.ok(Map.of(
                "paymentId", txn.getId().toString(),
                "status", txn.getStatus(),
                "txnRef", txn.getTxnRef()
        ));
    }

    @PostMapping("/{id}/capture")
    public ApiResponse<Map<String, String>> capture(@PathVariable UUID id) {
        PaymentTxn txn = payments.findById(id).orElseThrow(() -> DomainException.notFound("payment", id));
        if ("VOIDED".equals(txn.getStatus())) {
            throw DomainException.unprocessable("PAYMENT_VOIDED", "Cannot capture a voided payment");
        }
        txn.setStatus("CAPTURED");
        payments.save(txn);
        statusStore.put(id.toString(), "CAPTURED");
        return ApiResponse.ok(Map.of("paymentId", id.toString(), "status", "CAPTURED"));
    }

    @PostMapping("/{id}/void")
    public ApiResponse<Map<String, String>> voidPayment(@PathVariable UUID id) {
        PaymentTxn txn = payments.findById(id).orElseThrow(() -> DomainException.notFound("payment", id));
        txn.setStatus("VOIDED");
        payments.save(txn);
        statusStore.put(id.toString(), "VOIDED");
        return ApiResponse.ok(Map.of("paymentId", id.toString(), "status", "VOIDED"));
    }

    @PostMapping("/upi/bharat-qr")
    public ApiResponse<Map<String, Object>> qr(@RequestBody QrRequest request) {
        DynamicBharatQr qr = BharatQrFactory.create(request.vpa(), request.merchantName(), request.mcc(),
                request.orderId(), request.amount());
        UpiIntentResponse intents = BharatQrFactory.intents(qr.upiUri());
        PaymentTxn txn = new PaymentTxn();
        txn.setOrderId(parseOrderId(request.orderId()));
        txn.setAmountInr(request.amount());
        txn.setMode("UPI");
        txn.setStatus("PENDING");
        txn.setTxnRef(qr.txnId());
        payments.save(txn);
        statusStore.put(qr.txnId(), "PENDING");
        return ApiResponse.ok(Map.of(
                "paymentId", txn.getId().toString(),
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

    private static UUID parseOrderId(String orderId) {
        try {
            return UUID.fromString(orderId);
        } catch (Exception ex) {
            return UUID.nameUUIDFromBytes(orderId.getBytes());
        }
    }
}
