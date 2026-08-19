package com.ecs.common.core.http;

import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.ratelimiter.RateLimiterRegistry;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication;
import org.springframework.boot.web.client.RestClientCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET)
@ConditionalOnClass(RestClient.class)
public class EcsOutboundHttpConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public RateLimiterRegistry ecsRateLimiterRegistry() {
        return RateLimiterRegistry.ofDefaults();
    }

    @Bean
    @ConditionalOnMissingBean
    public CircuitBreakerRegistry ecsCircuitBreakerRegistry() {
        return CircuitBreakerRegistry.ofDefaults();
    }

    @Bean
    public DownstreamGuardInterceptor downstreamGuardInterceptor(
            RateLimiterRegistry rateLimiterRegistry,
            CircuitBreakerRegistry circuitBreakerRegistry
    ) {
        return new DownstreamGuardInterceptor(rateLimiterRegistry, circuitBreakerRegistry);
    }

    @Bean
    public RestClientCustomizer ecsDownstreamRestClientCustomizer(DownstreamGuardInterceptor interceptor) {
        return builder -> builder.requestInterceptor(interceptor);
    }

    @Bean
    @ConditionalOnMissingBean
    public RestClient ecsRestClient(RestClient.Builder builder) {
        return builder.build();
    }
}
