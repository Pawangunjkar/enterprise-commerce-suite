#!/usr/bin/env python3
"""Generate platform infrastructure Spring Boot services."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PI = ROOT / "platform-infrastructure"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


BOOT = '''
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
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
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
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
'''


def svc_pom(artifact, name, extra=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>platform-infrastructure</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <name>{name}</name>
    <dependencies>
        {BOOT}
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


def yml(app, port, db):
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
    open-in-view: false
    properties:
      hibernate.jdbc.time_zone: Asia/Kolkata
  flyway:
    enabled: true
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: {app}
      auto-offset-reset: earliest
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
'''


# ===== API GATEWAY =====
w(PI / "api-gateway/pom.xml", '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>platform-infrastructure</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>api-gateway</artifactId>
    <name>API Gateway</name>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-gateway</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis-reactive</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
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
''')

w(PI / "api-gateway/src/main/resources/application.yml", '''
server:
  port: 8080
spring:
  application:
    name: api-gateway
  data:
    redis:
      host: localhost
      port: 6379
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
  cloud:
    gateway:
      default-filters:
        - TokenRelay
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 40
            redis-rate-limiter.burstCapacity: 80
            key-resolver: "#{@ipKeyResolver}"
      routes:
        - id: search
          uri: http://localhost:8090
          predicates: [Path=/api/v1/search/**]
        - id: pincode
          uri: http://localhost:8091
          predicates: [Path=/api/v1/pincodes/**]
        - id: catalog
          uri: http://localhost:8101
          predicates: [Path=/api/v1/catalog/**, /api/v1/products/**, /api/v1/offers/**, /api/v1/imei/**]
        - id: oms
          uri: http://localhost:8201
          predicates: [Path=/api/v1/carts/**, /api/v1/checkout/**, /api/v1/orders/**, /api/v1/prices/**, /api/v1/wms/**]
        - id: billing
          uri: http://localhost:8301
          predicates: [Path=/api/v1/gst/**, /api/v1/payments/**, /api/v1/invoices/**, /api/v1/ledger/**, /api/v1/tcs/**]
        - id: crm
          uri: http://localhost:8401
          predicates: [Path=/api/v1/customers/**, /api/v1/tickets/**, /api/v1/assisted-sales/**, /api/v1/loyalty/**]
        - id: dlq
          uri: http://localhost:8092
          predicates: [Path=/api/v1/dlq/**]
        - id: audit
          uri: http://localhost:8093
          predicates: [Path=/api/v1/audit/**]
        - id: notify
          uri: http://localhost:8094
          predicates: [Path=/api/v1/notifications/**]
ecs:
  rate-limit:
    public-replenish: 80
    public-burst: 160
''')

w(PI / "api-gateway/src/main/java/com/ecs/gateway/ApiGatewayApplication.java", '''
package com.ecs.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ApiGatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
''')

w(PI / "api-gateway/src/main/java/com/ecs/gateway/config/GatewaySecurityConfig.java", '''
package com.ecs.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
public class GatewaySecurityConfig {

    @Bean
    public SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
        http.csrf(ServerHttpSecurity.CsrfSpec::disable)
                .authorizeExchange(ex -> ex
                        .pathMatchers("/actuator/**").permitAll()
                        .pathMatchers(HttpMethod.GET, "/api/v1/search/**", "/api/v1/pincodes/**", "/api/v1/catalog/public/**").permitAll()
                        .anyExchange().authenticated())
                .oauth2ResourceServer(oauth -> oauth.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
''')

w(PI / "api-gateway/src/main/java/com/ecs/gateway/filter/ClaimForwardingFilter.java", '''
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
''')

w(PI / "api-gateway/src/main/java/com/ecs/gateway/config/RateLimitConfig.java", '''
package com.ecs.gateway.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import reactor.core.publisher.Mono;

@Configuration
public class RateLimitConfig {

    @Bean
    public KeyResolver ipKeyResolver() {
        return exchange -> Mono.just(
                exchange.getRequest().getRemoteAddress() == null
                        ? "unknown"
                        : exchange.getRequest().getRemoteAddress().getAddress().getHostAddress()
        );
    }
}
''')

# ===== PINCODE =====
w(PI / "pincode-master-service/pom.xml", svc_pom("pincode-master-service", "Pincode Master Service"))
w(PI / "pincode-master-service/src/main/resources/application.yml", yml("pincode-master-service", 8091, "ecs_platform"))
w(PI / "pincode-master-service/src/main/java/com/ecs/pincode/PincodeMasterApplication.java", '''
package com.ecs.pincode;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class PincodeMasterApplication {
    public static void main(String[] args) {
        SpringApplication.run(PincodeMasterApplication.class, args);
    }
}
''')

w(PI / "pincode-master-service/src/main/java/com/ecs/pincode/domain/Pincode.java", '''
package com.ecs.pincode.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "pincode_master")
public class Pincode extends BaseEntity {

    @Column(nullable = false, unique = true, length = 6)
    private String pincode;

    @Column(nullable = false, length = 80)
    private String city;

    @Column(nullable = false, length = 80)
    private String district;

    @Column(nullable = false, length = 80)
    private String stateName;

    @Column(nullable = false, length = 2)
    private String stateCode;

    @Column(nullable = false)
    private boolean oda;

    @Column(nullable = false)
    private boolean serviceable = true;

    @Column(nullable = false)
    private int standardTransitDays = 4;

    public String getPincode() { return pincode; }
    public void setPincode(String pincode) { this.pincode = pincode; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }
    public String getStateName() { return stateName; }
    public void setStateName(String stateName) { this.stateName = stateName; }
    public String getStateCode() { return stateCode; }
    public void setStateCode(String stateCode) { this.stateCode = stateCode; }
    public boolean isOda() { return oda; }
    public void setOda(boolean oda) { this.oda = oda; }
    public boolean isServiceable() { return serviceable; }
    public void setServiceable(boolean serviceable) { this.serviceable = serviceable; }
    public int getStandardTransitDays() { return standardTransitDays; }
    public void setStandardTransitDays(int standardTransitDays) { this.standardTransitDays = standardTransitDays; }
}
''')

w(PI / "pincode-master-service/src/main/java/com/ecs/pincode/repo/PincodeRepository.java", '''
package com.ecs.pincode.repo;

import com.ecs.pincode.domain.Pincode;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface PincodeRepository extends JpaRepository<Pincode, UUID> {
    Optional<Pincode> findByPincode(String pincode);
}
''')

w(PI / "pincode-master-service/src/main/java/com/ecs/pincode/api/PincodeController.java", '''
package com.ecs.pincode.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.pincode.domain.Pincode;
import com.ecs.pincode.repo.PincodeRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/pincodes")
public class PincodeController {

    private final PincodeRepository repository;

    public PincodeController(PincodeRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/{pincode}")
    public ApiResponse<Pincode> get(@PathVariable String pincode) {
        return ApiResponse.ok(repository.findByPincode(pincode)
                .orElseThrow(() -> DomainException.notFound("Pincode", pincode)));
    }

    @GetMapping("/{pincode}/serviceability")
    public ApiResponse<Map<String, Object>> serviceability(
            @PathVariable String pincode,
            @RequestParam(defaultValue = "110001") String origin
    ) {
        Pincode dest = repository.findByPincode(pincode)
                .orElseThrow(() -> DomainException.notFound("Pincode", pincode));
        Pincode orig = repository.findByPincode(origin).orElse(dest);
        int days = dest.getStandardTransitDays();
        if (dest.isOda()) {
            days += 2;
        }
        if (!orig.getStateCode().equals(dest.getStateCode())) {
            days += 1;
        }
        LocalDate edd = LocalDate.now().plusDays(days);
        return ApiResponse.ok(Map.of(
                "pincode", dest.getPincode(),
                "serviceable", dest.isServiceable(),
                "oda", dest.isOda(),
                "city", dest.getCity(),
                "stateCode", dest.getStateCode(),
                "originStateCode", orig.getStateCode(),
                "intraState", orig.getStateCode().equals(dest.getStateCode()),
                "edd", edd.toString(),
                "transitDays", days
        ));
    }
}
''')

w(PI / "pincode-master-service/src/main/resources/db/migration/V1__pincode.sql", '''
CREATE TABLE IF NOT EXISTS pincode_master (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    pincode VARCHAR(6) NOT NULL UNIQUE,
    city VARCHAR(80) NOT NULL,
    district VARCHAR(80) NOT NULL,
    state_name VARCHAR(80) NOT NULL,
    state_code VARCHAR(2) NOT NULL,
    oda BOOLEAN NOT NULL DEFAULT FALSE,
    serviceable BOOLEAN NOT NULL DEFAULT TRUE,
    standard_transit_days INT NOT NULL DEFAULT 4
);

INSERT INTO pincode_master (id, created_at, updated_at, tenant_id, version, pincode, city, district, state_name, state_code, oda, serviceable, standard_transit_days)
VALUES
(gen_random_uuid(), now(), now(), 'default', 0, '110001', 'New Delhi', 'New Delhi', 'Delhi', 'DL', false, true, 2),
(gen_random_uuid(), now(), now(), 'default', 0, '400001', 'Mumbai', 'Mumbai', 'Maharashtra', 'MH', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '560001', 'Bengaluru', 'Bengaluru', 'Karnataka', 'KA', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '600001', 'Chennai', 'Chennai', 'Tamil Nadu', 'TN', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '700001', 'Kolkata', 'Kolkata', 'West Bengal', 'WB', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '500001', 'Hyderabad', 'Hyderabad', 'Telangana', 'TS', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '380001', 'Ahmedabad', 'Ahmedabad', 'Gujarat', 'GJ', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '302001', 'Jaipur', 'Jaipur', 'Rajasthan', 'RJ', false, true, 5),
(gen_random_uuid(), now(), now(), 'default', 0, '226001', 'Lucknow', 'Lucknow', 'Uttar Pradesh', 'UP', false, true, 5),
(gen_random_uuid(), now(), now(), 'default', 0, '141001', 'Ludhiana', 'Ludhiana', 'Punjab', 'PB', true, true, 6)
ON CONFLICT DO NOTHING;
''')

print("gateway + pincode done")
