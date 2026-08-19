package com.ecs.billing.pay.ws;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class PaymentWebSocketConfig implements WebSocketConfigurer {

    private final PaymentStatusSocketHandler handler;

    public PaymentWebSocketConfig(PaymentStatusSocketHandler handler) {
        this.handler = handler;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(handler, "/ws/payments/*").setAllowedOrigins("*");
    }
}
