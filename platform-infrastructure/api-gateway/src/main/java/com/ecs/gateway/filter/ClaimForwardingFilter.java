package com.ecs.gateway.filter;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class ClaimForwardingFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        return exchange.getPrincipal()
                .filter(JwtAuthenticationToken.class::isInstance)
                .cast(JwtAuthenticationToken.class)
                .map(JwtAuthenticationToken::getToken)
                .defaultIfEmpty(dummy())
                .flatMap(jwt -> {
                    if ("anonymous".equals(jwt.getSubject())) {
                        return chain.filter(exchange);
                    }
                    var mutated = exchange.mutate().request(builder -> builder
                            .header("X-User-Id", str(jwt, "sub"))
                            .header("X-Tenant-Id", str(jwt, "tenant_id"))
                            .header("X-User-Roles", join(jwt, "realm_access"))
                            .header("X-Scopes", String.join(",", jwt.getClaimAsStringList("scope") == null
                                    ? List.of() : jwt.getClaimAsStringList("scope")))
                            .header("X-User-Mobile", str(jwt, "mobile"))
                            .header("X-User-Email", str(jwt, "email"))
                    ).build();
                    return chain.filter(mutated);
                });
    }

    private Jwt dummy() {
        return Jwt.withTokenValue("anonymous")
                .header("alg", "none")
                .subject("anonymous")
                .claim("tenant_id", "default")
                .build();
    }

    private String str(Jwt jwt, String claim) {
        Object value = jwt.getClaim(claim);
        return value == null ? "" : String.valueOf(value);
    }

    @SuppressWarnings("unchecked")
    private String join(Jwt jwt, String claim) {
        Object realm = jwt.getClaim(claim);
        if (realm instanceof java.util.Map<?, ?> map) {
            Object roles = map.get("roles");
            if (roles instanceof Collection<?> col) {
                return col.stream().map(String::valueOf).collect(Collectors.joining(","));
            }
        }
        return "";
    }

    @Override
    public int getOrder() {
        return -1;
    }
}
