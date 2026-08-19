package com.ecs.common.core.exception;

import org.springframework.http.HttpStatus;

public class DomainException extends RuntimeException {
    private final HttpStatus status;
    private final String code;

    public DomainException(HttpStatus status, String code, String message) {
        super(message);
        this.status = status;
        this.code = code;
    }

    public static DomainException notFound(String resource, Object id) {
        return new DomainException(HttpStatus.NOT_FOUND, "NOT_FOUND", resource + " not found: " + id);
    }

    public static DomainException conflict(String message) {
        return new DomainException(HttpStatus.CONFLICT, "CONFLICT", message);
    }

    public static DomainException badRequest(String message) {
        return new DomainException(HttpStatus.BAD_REQUEST, "BAD_REQUEST", message);
    }

    public static DomainException unprocessable(String code, String message) {
        return new DomainException(HttpStatus.UNPROCESSABLE_ENTITY, code, message);
    }

    public HttpStatus getStatus() { return status; }
    public String getCode() { return code; }
}
