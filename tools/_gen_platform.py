#!/usr/bin/env python3
"""Generate platform-infrastructure POMs, shared libraries, and infra services."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PI = ROOT / "platform-infrastructure"
SL = PI / "shared-libraries"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


SPRING_PARENT = """
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>enterprise-commerce-suite</artifactId>
        <version>1.0.0-SNAPSHOT</version>
        <relativePath>../../pom.xml</relativePath>
    </parent>
""".strip()

LIB_PARENT = """
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>shared-libraries</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
""".strip()

BOOT_DEPS = """
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.6.0</version>
        </dependency>
        <dependency>
            <groupId>com.ecs</groupId>
            <artifactId>common-core</artifactId>
        </dependency>
        <dependency>
            <groupId>com.ecs</groupId>
            <artifactId>common-security</artifactId>
        </dependency>
        <dependency>
            <groupId>com.ecs</groupId>
            <artifactId>common-events</artifactId>
        </dependency>
"""


def lib_pom(artifact: str, name: str, extra: str = "") -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    {LIB_PARENT}
    <artifactId>{artifact}</artifactId>
    <name>{name}</name>
    <dependencies>
        {extra}
    </dependencies>
</project>
'''


def svc_pom(rel_parent: str, artifact: str, name: str, extra: str = "") -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>{rel_parent}</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <name>{name}</name>
    <dependencies>
        {BOOT_DEPS}
        {extra}
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''


def yml(app: str, port: int, db: str) -> str:
    return f'''server:
  port: {port}
spring:
  application:
    name: {app}
  datasource:
    url: jdbc:postgresql://localhost:5432/{db}
    username: ecs
    password: ecs_secret
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        jdbc:
          time_zone: Asia/Kolkata
        format_sql: true
  flyway:
    enabled: true
    locations: classpath:db/migration
  kafka:
    bootstrap-servers: localhost:9092
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  tracing:
    sampling:
      probability: 1.0
ecs:
  tenant:
    header: X-Tenant-Id
  security:
    jwt:
      issuer-uri: http://localhost:8081/realms/ecs
'''


# ---------- parent POMs ----------
w(PI / "pom.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>enterprise-commerce-suite</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>platform-infrastructure</artifactId>
    <packaging>pom</packaging>
    <name>Platform Infrastructure</name>
    <modules>
        <module>shared-libraries</module>
        <module>api-gateway</module>
        <module>search-solr-indexer</module>
        <module>notification-service</module>
        <module>kafka-dlq-manager</module>
        <module>pincode-master-service</module>
        <module>mca-audit-trail-service</module>
    </modules>
</project>
''')

w(SL / "pom.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>platform-infrastructure</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>shared-libraries</artifactId>
    <packaging>pom</packaging>
    <name>Shared Libraries</name>
    <modules>
        <module>common-core</module>
        <module>common-security</module>
        <module>common-events</module>
        <module>payment-spi</module>
        <module>logistics-spi</module>
        <module>ondc-beckn-spi</module>
        <module>saga-orchestration</module>
    </modules>
</project>
''')

# ---------- common-core ----------
core_deps = '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>
'''
w(SL / "common-core/pom.xml", lib_pom("common-core", "Common Core", core_deps))

w(SL / "common-core/src/main/java/com/ecs/common/core/domain/BaseEntity.java", '''
package com.ecs.common.core.domain;

import jakarta.persistence.Column;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.Id;
import jakarta.persistence.MappedSuperclass;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Version;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;
import java.util.UUID;

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @Column(nullable = false, updatable = false, columnDefinition = "uuid")
    private UUID id;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private Instant updatedAt;

    @CreatedBy
    @Column(updatable = false, length = 128)
    private String createdBy;

    @LastModifiedBy
    @Column(length = 128)
    private String updatedBy;

    @Column(nullable = false, length = 64)
    private String tenantId = "default";

    @Version
    private long version;

    @PrePersist
    void assignId() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        Instant now = Instant.now();
        if (createdAt == null) {
            createdAt = now;
        }
        if (updatedAt == null) {
            updatedAt = now;
        }
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public String getCreatedBy() { return createdBy; }
    public String getUpdatedBy() { return updatedBy; }
    public String getTenantId() { return tenantId; }
    public void setTenantId(String tenantId) { this.tenantId = tenantId; }
    public long getVersion() { return version; }
}
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/api/ApiResponse.java", '''
package com.ecs.common.core.api;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record ApiResponse<T>(boolean success, T data, String message, Instant timestamp) {

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(true, data, null, Instant.now());
    }

    public static <T> ApiResponse<T> ok(T data, String message) {
        return new ApiResponse<>(true, data, message, Instant.now());
    }

    public static <T> ApiResponse<T> failure(String message) {
        return new ApiResponse<>(false, null, message, Instant.now());
    }
}
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/api/PageResponse.java", '''
package com.ecs.common.core.api;

import org.springframework.data.domain.Page;

import java.util.List;

public record PageResponse<T>(
        List<T> content,
        int page,
        int size,
        long totalElements,
        int totalPages,
        boolean last
) {
    public static <T> PageResponse<T> from(Page<T> page) {
        return new PageResponse<>(
                page.getContent(),
                page.getNumber(),
                page.getSize(),
                page.getTotalElements(),
                page.getTotalPages(),
                page.isLast()
        );
    }
}
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/exception/DomainException.java", '''
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
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/exception/GlobalExceptionHandler.java", '''
package com.ecs.common.core.exception;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;
import java.time.Instant;
import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ProblemDetail> handleDomain(DomainException ex, HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(ex.getStatus(), ex.getMessage());
        problem.setTitle(ex.getCode());
        problem.setType(URI.create("https://ecs.local/problems/" + ex.getCode().toLowerCase()));
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("path", request.getRequestURI());
        return ResponseEntity.status(ex.getStatus()).body(problem);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException ex, HttpServletRequest request) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .collect(Collectors.joining("; "));
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        problem.setTitle("VALIDATION_FAILED");
        problem.setType(URI.create("https://ecs.local/problems/validation"));
        problem.setProperty("path", request.getRequestURI());
        return ResponseEntity.badRequest().body(problem);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ProblemDetail> handleConstraint(ConstraintViolationException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setTitle("CONSTRAINT_VIOLATION");
        return ResponseEntity.badRequest().body(problem);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ProblemDetail> handleUnknown(Exception ex, HttpServletRequest request) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected server error");
        problem.setTitle("INTERNAL_ERROR");
        problem.setProperty("path", request.getRequestURI());
        problem.setProperty("timestamp", Instant.now());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(problem);
    }
}
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/config/JpaAuditingConfig.java", '''
package com.ecs.common.core.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.Optional;

@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorAware")
public class JpaAuditingConfig {

    @Bean
    public AuditorAware<String> auditorAware() {
        return () -> {
            var attrs = RequestContextHolder.getRequestAttributes();
            if (attrs instanceof ServletRequestAttributes servlet) {
                String user = servlet.getRequest().getHeader("X-User-Id");
                if (user != null && !user.isBlank()) {
                    return Optional.of(user);
                }
            }
            return Optional.of("system");
        };
    }
}
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/tenant/TenantContext.java", '''
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
''')

w(SL / "common-core/src/main/java/com/ecs/common/core/tenant/TenantFilter.java", '''
package com.ecs.common.core.tenant;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class TenantFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        try {
            TenantContext.set(request.getHeader("X-Tenant-Id"));
            filterChain.doFilter(request, response);
        } finally {
            TenantContext.clear();
        }
    }
}
''')

print("common-core written")
print("ROOT", ROOT)
