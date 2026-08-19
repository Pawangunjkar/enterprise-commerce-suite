package com.ecs.billing.pay.ws;

import com.ecs.billing.pay.PaymentStatusStore;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

@Component
public class PaymentStatusSocketHandler extends TextWebSocketHandler {

    private final PaymentStatusStore statusStore;

    public PaymentStatusSocketHandler(PaymentStatusStore statusStore) {
        this.statusStore = statusStore;
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        String path = session.getUri() == null ? "" : session.getUri().getPath();
        String txnId = path.substring(path.lastIndexOf('/') + 1);
        session.sendMessage(new TextMessage("{\"txnId\":\"" + txnId + "\",\"status\":\"" + statusStore.get(txnId) + "\"}"));
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String path = session.getUri() == null ? "" : session.getUri().getPath();
        String txnId = path.substring(path.lastIndexOf('/') + 1);
        session.sendMessage(new TextMessage("{\"txnId\":\"" + txnId + "\",\"status\":\"" + statusStore.get(txnId) + "\"}"));
    }
}
