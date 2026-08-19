package com.ecs.billing.pay;

import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class PaymentStatusStore {
    private final ConcurrentHashMap<String, String> status = new ConcurrentHashMap<>();

    public void put(String txnId, String value) {
        status.put(txnId, value);
    }

    public String get(String txnId) {
        return status.getOrDefault(txnId, "UNKNOWN");
    }

    public Map<String, String> snapshot() {
        return Map.copyOf(status);
    }
}
