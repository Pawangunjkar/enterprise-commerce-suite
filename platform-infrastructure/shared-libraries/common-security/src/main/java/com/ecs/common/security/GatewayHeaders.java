package com.ecs.common.security;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public final class GatewayHeaders {
    public static final String USER_ID = "X-User-Id";
    public static final String TENANT_ID = "X-Tenant-Id";
    public static final String USER_ROLES = "X-User-Roles";
    public static final String SCOPES = "X-Scopes";
    public static final String MOBILE = "X-User-Mobile";
    public static final String EMAIL = "X-User-Email";

    private GatewayHeaders() {}

    public static GatewayPrincipal current() {
        HttpServletRequest request = request();
        UUID userId = Optional.ofNullable(request.getHeader(USER_ID))
                .filter(s -> !s.isBlank())
                .map(UUID::fromString)
                .orElse(null);
        return new GatewayPrincipal(
                userId,
                Optional.ofNullable(request.getHeader(TENANT_ID)).orElse("default"),
                split(request.getHeader(USER_ROLES)),
                split(request.getHeader(SCOPES)),
                request.getHeader(MOBILE),
                request.getHeader(EMAIL)
        );
    }

    private static List<String> split(String value) {
        if (value == null || value.isBlank()) {
            return List.of();
        }
        return Arrays.stream(value.split(",")).map(String::trim).filter(s -> !s.isEmpty()).toList();
    }

    private static HttpServletRequest request() {
        var attrs = RequestContextHolder.getRequestAttributes();
        if (attrs instanceof ServletRequestAttributes servlet) {
            return servlet.getRequest();
        }
        throw new IllegalStateException("No HTTP request bound to the current thread");
    }
}
