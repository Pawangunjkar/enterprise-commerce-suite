package com.ecs.common.security;

import java.util.List;
import java.util.UUID;

public record GatewayPrincipal(
        UUID userId,
        String tenantId,
        List<String> roles,
        List<String> scopes,
        String mobile,
        String email
) {
    public boolean hasRole(String role) {
        return roles != null && roles.stream().anyMatch(r -> r.equalsIgnoreCase(role) || r.equalsIgnoreCase("ROLE_" + role));
    }

    public boolean hasScope(String scope) {
        return scopes != null && scopes.contains(scope);
    }
}
