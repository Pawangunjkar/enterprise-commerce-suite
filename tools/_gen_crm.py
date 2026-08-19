#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRM = ROOT / "customer-relationship-management"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


mods = [
    "customer-360-service", "assisted-sales-service", "account-hierarchy-service",
    "contact-address-service", "support-ticket-service", "loyalty-rewards-service",
    "cart-abandonment-service", "dpdp-compliance-service"
]
modxml = "\n".join(f"        <module>{m}</module>" for m in mods)
w(CRM / "pom.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>enterprise-commerce-suite</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>customer-relationship-management</artifactId>
    <packaging>pom</packaging>
    <name>Customer Relationship Management</name>
    <modules>
{modxml}
    </modules>
</project>
''')


def svc_pom(artifact):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>customer-relationship-management</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        <dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka</artifactId></dependency>
        <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
        <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>
        <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>
        <dependency><groupId>org.springdoc</groupId><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId><version>2.6.0</version></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-core</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-security</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-events</artifactId></dependency>
    </dependencies>
    <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
'''


def yml(app, port):
    return f'''server:
  port: {port}
spring:
  application:
    name: {app}
  datasource:
    url: jdbc:postgresql://localhost:5432/ecs_crm
    username: ecs
    password: ecs_secret
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true
  kafka:
    bootstrap-servers: localhost:9092
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
'''


def boot(mod, pkg, cls, port, controller):
    w(CRM / f"{mod}/pom.xml", svc_pom(mod))
    w(CRM / f"{mod}/src/main/resources/application.yml", yml(mod, port))
    w(CRM / f"{mod}/src/main/java/{pkg.replace('.', '/')}/{cls}.java", f'''
package {pkg};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class {cls} {{
    public static void main(String[] args) {{ SpringApplication.run({cls}.class, args); }}
}}
''')
    w(CRM / f"{mod}/src/main/java/{pkg.replace('.', '/')}/api/Api.java", controller)


boot("customer-360-service", "com.ecs.crm.customer", "Customer360Application", 8401, '''
package com.ecs.crm.customer.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
@RestController
@RequestMapping("/api/v1/customers")
public class Api {
    private final Map<String, Map<String, Object>> store = new ConcurrentHashMap<>();
    public record OtpStart(String mobile) {}
    public record OtpVerify(String mobile, String otp) {}
    public record Profile(String mobile, String pan, String gstin, String name) {}

    @PostMapping("/otp/start")
    public ApiResponse<Map<String, String>> start(@RequestBody OtpStart request) {
        if (request.mobile() == null || !request.mobile().matches("^[6-9]\\\\d{9}$")) {
            throw DomainException.badRequest("Invalid Indian mobile number");
        }
        store.put(request.mobile(), Map.of("otp", "123456"));
        return ApiResponse.ok(Map.of("status", "OTP_SENT"));
    }

    @PostMapping("/otp/verify")
    public ApiResponse<Map<String, Object>> verify(@RequestBody OtpVerify request) {
        if (!"123456".equals(request.otp())) throw DomainException.unprocessable("OTP_INVALID", "Incorrect OTP");
        return ApiResponse.ok(Map.of("mobile", request.mobile(), "kycStatus", "PENDING"));
    }

    @PutMapping("/{mobile}")
    public ApiResponse<Profile> upsert(@PathVariable String mobile, @RequestBody Profile profile) {
        return ApiResponse.ok(new Profile(mobile, profile.pan(), profile.gstin(), profile.name()));
    }
}
''')

boot("assisted-sales-service", "com.ecs.crm.assisted", "AssistedSalesApplication", 8402, '''
package com.ecs.crm.assisted.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.UUID;
@RestController
@RequestMapping("/api/v1/assisted-sales")
public class Api {
    @PostMapping("/paylinks")
    public ApiResponse<Map<String, String>> paylink(@RequestBody Map<String, String> body) {
        String token = UUID.randomUUID().toString();
        return ApiResponse.ok(Map.of(
                "customerMobile", body.get("mobile"),
                "paylink", "https://shop.ecs.local/pay/" + token,
                "channel", "WHATSAPP"
        ));
    }
}
''')

boot("account-hierarchy-service", "com.ecs.crm.hierarchy", "AccountHierarchyApplication", 8403, '''
package com.ecs.crm.hierarchy.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/accounts")
public class Api {
    @GetMapping("/tree")
    public ApiResponse<Map<String, Object>> tree() {
        return ApiResponse.ok(Map.of(
                "name", "Acme India Pvt Ltd",
                "gstin", "07AABCU9603R1ZM",
                "children", List.of(
                        Map.of("name", "North Region", "children", List.of(Map.of("name", "Delhi Branch"))),
                        Map.of("name", "West Region", "children", List.of(Map.of("name", "Mumbai Branch")))
                )
        ));
    }
}
''')

boot("contact-address-service", "com.ecs.crm.address", "ContactAddressApplication", 8404, '''
package com.ecs.crm.address.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/addresses")
public class Api {
    @GetMapping("/autofill")
    public ApiResponse<Map<String, String>> autofill(@RequestParam String pincode) {
        return ApiResponse.ok(Map.of("pincode", pincode, "city", "New Delhi", "state", "Delhi", "stateCode", "DL"));
    }
}
''')

boot("support-ticket-service", "com.ecs.crm.ticket", "SupportTicketApplication", 8405, '''
package com.ecs.crm.ticket.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
@RestController
@RequestMapping("/api/v1/tickets")
public class Api {
    @PostMapping
    public ApiResponse<Map<String, Object>> create(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of(
                "ticketId", UUID.randomUUID().toString(),
                "priority", body.getOrDefault("priority", "P2"),
                "slaDueAt", Instant.now().plusSeconds(14400).toString(),
                "status", "OPEN"
        ));
    }
}
''')

boot("loyalty-rewards-service", "com.ecs.crm.loyalty", "LoyaltyRewardsApplication", 8406, '''
package com.ecs.crm.loyalty.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/loyalty")
public class Api {
    @GetMapping("/{customerId}")
    public ApiResponse<Map<String, Object>> get(@PathVariable String customerId, @RequestParam(defaultValue = "1.0") double festivalMultiplier) {
        return ApiResponse.ok(Map.of("customerId", customerId, "tier", "GOLD", "points", 4200, "festivalMultiplier", festivalMultiplier,
                "redeemableInr", new BigDecimal("420.00")));
    }
}
''')

boot("cart-abandonment-service", "com.ecs.crm.abandon", "CartAbandonmentApplication", 8407, '''
package com.ecs.crm.abandon.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.events.Topics;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/carts/abandonment")
public class Api {
    private final KafkaTemplate<String, String> kafka;
    public Api(KafkaTemplate<String, String> kafka) { this.kafka = kafka; }
    @PostMapping
    public ApiResponse<Map<String, String>> mark(@RequestBody Map<String, String> body) {
        kafka.send(Topics.CART_ABANDONED, body.get("cartId"), body.toString());
        return ApiResponse.ok(Map.of("status", "RECOVERY_QUEUED", "channel", "WHATSAPP"));
    }
}
''')

boot("dpdp-compliance-service", "com.ecs.crm.dpdp", "DpdpComplianceApplication", 8408, '''
package com.ecs.crm.dpdp.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/dpdp")
public class Api {
    @PostMapping("/consent")
    public ApiResponse<Map<String, Object>> consent(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of("principal", body.get("mobile"), "purpose", body.get("purpose"),
                "grantedAt", Instant.now().toString(), "law", "DPDP Act 2023"));
    }
    @PostMapping("/anonymize/{customerId}")
    public ApiResponse<Map<String, String>> anonymize(@PathVariable String customerId) {
        return ApiResponse.ok(Map.of("customerId", customerId, "status", "ANONYMIZED"));
    }
}
''')

print("CRM generated")
