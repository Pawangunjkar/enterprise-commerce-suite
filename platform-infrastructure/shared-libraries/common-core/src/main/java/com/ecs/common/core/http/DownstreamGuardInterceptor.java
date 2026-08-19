package com.ecs.common.core.http;

import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RateLimiterConfig;
import io.github.resilience4j.ratelimiter.RateLimiterRegistry;
import io.github.resilience4j.ratelimiter.RequestNotPermitted;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;

import java.io.IOException;
import java.time.Duration;
import java.util.function.Supplier;

/**
 * Limits and isolates outbound HTTP calls to other microservices (per host:port).
 */
public class DownstreamGuardInterceptor implements ClientHttpRequestInterceptor {

    private final RateLimiterRegistry rateLimiters;
    private final CircuitBreakerRegistry circuitBreakers;

    public DownstreamGuardInterceptor(RateLimiterRegistry rateLimiters, CircuitBreakerRegistry circuitBreakers) {
        this.rateLimiters = rateLimiters;
        this.circuitBreakers = circuitBreakers;
    }

    @Override
    public ClientHttpResponse intercept(HttpRequest request, byte[] body, ClientHttpRequestExecution execution)
            throws IOException {
        String name = downstreamName(request);
        RateLimiter limiter = rateLimiters.rateLimiter(name, RateLimiterConfig.custom()
                .limitForPeriod(80)
                .limitRefreshPeriod(Duration.ofSeconds(1))
                .timeoutDuration(Duration.ofMillis(250))
                .build());
        CircuitBreaker breaker = circuitBreakers.circuitBreaker(name, CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .slidingWindowSize(20)
                .waitDurationInOpenState(Duration.ofSeconds(5))
                .build());
        Supplier<ClientHttpResponse> call = CircuitBreaker.decorateSupplier(
                breaker,
                RateLimiter.decorateSupplier(limiter, () -> {
                    try {
                        return execution.execute(request, body);
                    } catch (IOException ex) {
                        throw new DownstreamIoException(ex);
                    }
                }));
        try {
            return call.get();
        } catch (RequestNotPermitted ex) {
            throw new IOException("Outbound rate limit exceeded for " + name, ex);
        } catch (CallNotPermittedException ex) {
            throw new IOException("Circuit open for downstream " + name, ex);
        } catch (DownstreamIoException ex) {
            throw ex.getCauseIo();
        }
    }

    private static String downstreamName(HttpRequest request) {
        var uri = request.getURI();
        String host = uri.getHost() == null ? "unknown" : uri.getHost();
        int port = uri.getPort() == -1 ? 80 : uri.getPort();
        return host + ":" + port;
    }

    private static final class DownstreamIoException extends RuntimeException {
        private DownstreamIoException(IOException cause) {
            super(cause);
        }

        private IOException getCauseIo() {
            return (IOException) getCause();
        }
    }
}
