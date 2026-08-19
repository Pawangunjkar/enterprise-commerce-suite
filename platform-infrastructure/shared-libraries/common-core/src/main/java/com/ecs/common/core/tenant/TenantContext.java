package com.ecs.common.core.tenant;

public final class TenantContext {
    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();

    private TenantContext() {}

    public static void set(String tenantId) {
        CURRENT.set(tenantId == null || tenantId.isBlank() ? "default" : tenantId);
    }

    public static String get() {
        String value = CURRENT.get();
        return value == null ? "default" : value;
    }

    public static void clear() {
        CURRENT.remove();
    }
}
