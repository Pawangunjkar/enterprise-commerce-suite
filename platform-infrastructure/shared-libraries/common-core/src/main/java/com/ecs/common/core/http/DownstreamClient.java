package com.ecs.common.core.http;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * Typed helper for service-to-service calls. Every request is rate-limited and circuit-broken.
 */
@Component
@ConditionalOnBean(RestClient.class)
public class DownstreamClient {

    private final RestClient restClient;
    private final String gatewayBase;

    public DownstreamClient(
            RestClient restClient,
            @Value("${ecs.downstream.gateway-url:http://localhost:8080}") String gatewayBase
    ) {
        this.restClient = restClient;
        this.gatewayBase = gatewayBase.endsWith("/") ? gatewayBase.substring(0, gatewayBase.length() - 1) : gatewayBase;
    }

    public <T> T getUrl(String url, Class<T> type) {
        return restClient.get().uri(url).retrieve().body(type);
    }

    public <T> T get(String path, Class<T> type) {
        return restClient.get().uri(gatewayBase + path).retrieve().body(type);
    }

    public <T> T post(String path, Object body, Class<T> type) {
        return restClient.post().uri(gatewayBase + path).body(body).retrieve().body(type);
    }
}
