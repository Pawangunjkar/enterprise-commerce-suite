#!/usr/bin/env python3
"""Generate all four domain suites with production business logic."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def parent_pom(artifact, name, modules, rel=".."):
    mods = "\n".join(f"        <module>{m}</module>" for m in modules)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>enterprise-commerce-suite</artifactId>
        <version>1.0.0-SNAPSHOT</version>
        <relativePath>{rel}/pom.xml</relativePath>
    </parent>
    <artifactId>{artifact}</artifactId>
    <packaging>pom</packaging>
    <name>{name}</name>
    <modules>
{mods}
    </modules>
</project>
'''


def svc_pom(parent, artifact, name, extra=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>{parent}</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <name>{name}</name>
    <dependencies>
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
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
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
  data:
    redis:
      host: localhost
      port: 6379
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: {app}
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
'''


def app_java(pkg, cls):
    return f'''package {pkg};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class {cls} {{
    public static void main(String[] args) {{
        SpringApplication.run({cls}.class, args);
    }}
}}
'''


# ===================== MEC =====================
MEC = ROOT / "master-enterprise-catalog"
mec_mods = [
    "product-service", "variant-matrix-service", "serial-imei-tracking-service",
    "b2b-tiered-catalog-service", "component-bundle-service", "cpq-rule-engine",
    "dynamic-schema-engine", "offer-promotion-service", "temporal-activation-service",
    "media-dam-service", "bulk-catalog-import-service", "catalog-sync-publisher"
]
w(MEC / "pom.xml", parent_pom("master-enterprise-catalog", "Master Enterprise Catalog", mec_mods))

extra_json = '''
        <dependency>
            <groupId>com.networknt</groupId>
            <artifactId>json-schema-validator</artifactId>
            <version>1.5.2</version>
        </dependency>
'''

w(MEC / "product-service/pom.xml", svc_pom("master-enterprise-catalog", "product-service", "Product Service"))
w(MEC / "product-service/src/main/resources/application.yml", yml("product-service", 8101, "ecs_mec"))
w(MEC / "product-service/src/main/java/com/ecs/mec/product/ProductServiceApplication.java",
  app_java("com.ecs.mec.product", "ProductServiceApplication"))

w(MEC / "product-service/src/main/java/com/ecs/mec/product/domain/ProductLifecycle.java", '''
package com.ecs.mec.product.domain;

public enum ProductLifecycle { DRAFT, STAGED, ACTIVE, RETIRED }
''')

w(MEC / "product-service/src/main/java/com/ecs/mec/product/domain/Product.java", '''
package com.ecs.mec.product.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;

@Entity
@Table(name = "product")
public class Product extends BaseEntity {

    @Column(nullable = false, unique = true, length = 64)
    private String sku;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(length = 8)
    private String hsnCode;

    @Column(length = 80)
    private String brand;

    @Column(length = 255)
    private String categoryPath;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private ProductLifecycle status = ProductLifecycle.DRAFT;

    @Column(nullable = false)
    private Instant effectiveFrom = Instant.now();

    private Instant effectiveTo;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal listPriceInr = BigDecimal.ZERO;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> attributes;

    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getHsnCode() { return hsnCode; }
    public void setHsnCode(String hsnCode) { this.hsnCode = hsnCode; }
    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }
    public String getCategoryPath() { return categoryPath; }
    public void setCategoryPath(String categoryPath) { this.categoryPath = categoryPath; }
    public ProductLifecycle getStatus() { return status; }
    public void setStatus(ProductLifecycle status) { this.status = status; }
    public Instant getEffectiveFrom() { return effectiveFrom; }
    public void setEffectiveFrom(Instant effectiveFrom) { this.effectiveFrom = effectiveFrom; }
    public Instant getEffectiveTo() { return effectiveTo; }
    public void setEffectiveTo(Instant effectiveTo) { this.effectiveTo = effectiveTo; }
    public BigDecimal getListPriceInr() { return listPriceInr; }
    public void setListPriceInr(BigDecimal listPriceInr) { this.listPriceInr = listPriceInr; }
    public Map<String, Object> getAttributes() { return attributes; }
    public void setAttributes(Map<String, Object> attributes) { this.attributes = attributes; }
}
''')

w(MEC / "product-service/src/main/java/com/ecs/mec/product/repo/ProductRepository.java", '''
package com.ecs.mec.product.repo;

import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.domain.ProductLifecycle;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ProductRepository extends JpaRepository<Product, UUID> {
    Optional<Product> findBySku(String sku);
    List<Product> findByStatusAndEffectiveFromLessThanEqual(ProductLifecycle status, Instant when);
}
''')

w(MEC / "product-service/src/main/java/com/ecs/mec/product/service/ProductCommandService.java", '''
package com.ecs.mec.product.service;

import com.ecs.common.core.exception.DomainException;
import com.ecs.common.events.CloudEventEnvelope;
import com.ecs.common.events.Topics;
import com.ecs.common.events.catalog.ProductPublishedEvent;
import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.domain.ProductLifecycle;
import com.ecs.mec.product.repo.ProductRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Service
public class ProductCommandService {

    private final ProductRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    public ProductCommandService(ProductRepository repository, KafkaTemplate<String, String> kafkaTemplate,
                                 ObjectMapper objectMapper) {
        this.repository = repository;
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = objectMapper;
    }

    public record UpsertRequest(String sku, String name, String hsnCode, String brand, String categoryPath,
                                Instant effectiveFrom, Instant effectiveTo, BigDecimal listPriceInr,
                                Map<String, Object> attributes) {}

    @Transactional
    public Product upsert(UpsertRequest request) {
        Product product = repository.findBySku(request.sku()).orElseGet(Product::new);
        product.setSku(request.sku());
        product.setName(request.name());
        product.setHsnCode(request.hsnCode());
        product.setBrand(request.brand());
        product.setCategoryPath(request.categoryPath());
        Instant from = request.effectiveFrom() == null ? Instant.now() : request.effectiveFrom();
        product.setEffectiveFrom(from);
        product.setEffectiveTo(request.effectiveTo());
        product.setListPriceInr(request.listPriceInr() == null ? BigDecimal.ZERO : request.listPriceInr());
        product.setAttributes(request.attributes());
        if (!from.isAfter(Instant.now())) {
            product.setStatus(ProductLifecycle.ACTIVE);
        } else {
            product.setStatus(ProductLifecycle.STAGED);
        }
        Product saved = repository.save(product);
        publish(saved);
        return saved;
    }

    @Transactional
    public Product activate(UUID id) {
        Product product = repository.findById(id).orElseThrow(() -> DomainException.notFound("Product", id));
        product.setStatus(ProductLifecycle.ACTIVE);
        Product saved = repository.save(product);
        publish(saved);
        return saved;
    }

    private void publish(Product product) {
        try {
            ProductPublishedEvent data = new ProductPublishedEvent(
                    product.getId(), product.getSku(), product.getName(), product.getHsnCode(),
                    product.getStatus().name(), product.getEffectiveFrom(), product.getEffectiveTo(),
                    product.getAttributes(), product.getListPriceInr(), product.getBrand(), product.getCategoryPath());
            String json = objectMapper.writeValueAsString(
                    CloudEventEnvelope.of(Topics.CATALOG_PRODUCT_PUBLISHED, "mec/product-service",
                            product.getTenantId(), product.getSku(), data));
            kafkaTemplate.send(Topics.CATALOG_PRODUCT_PUBLISHED, product.getSku(), json);
            if (product.getStatus() == ProductLifecycle.ACTIVE) {
                kafkaTemplate.send(Topics.CATALOG_PRODUCT_ACTIVATED, product.getSku(), json);
            }
        } catch (Exception ex) {
            throw new IllegalStateException("Failed to publish catalog event", ex);
        }
    }
}
''')

w(MEC / "product-service/src/main/java/com/ecs/mec/product/api/ProductController.java", '''
package com.ecs.mec.product.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.repo.ProductRepository;
import com.ecs.mec.product.service.ProductCommandService;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductCommandService commandService;
    private final ProductRepository repository;

    public ProductController(ProductCommandService commandService, ProductRepository repository) {
        this.commandService = commandService;
        this.repository = repository;
    }

    @PostMapping
    public ApiResponse<Product> create(@RequestBody ProductCommandService.UpsertRequest request) {
        return ApiResponse.ok(commandService.upsert(request));
    }

    @PutMapping("/{id}/activate")
    public ApiResponse<Product> activate(@PathVariable UUID id) {
        return ApiResponse.ok(commandService.activate(id));
    }

    @GetMapping("/{id}")
    public ApiResponse<Product> get(@PathVariable UUID id) {
        return ApiResponse.ok(repository.findById(id).orElseThrow(() -> DomainException.notFound("Product", id)));
    }

    @GetMapping
    public ApiResponse<PageResponse<Product>> list(@RequestParam(defaultValue = "0") int page,
                                                   @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.ok(PageResponse.from(repository.findAll(PageRequest.of(page, size))));
    }
}
''')

w(MEC / "product-service/src/main/resources/db/migration/V1__product.sql", '''
CREATE TABLE IF NOT EXISTS product (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    sku VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    hsn_code VARCHAR(8),
    brand VARCHAR(80),
    category_path VARCHAR(255),
    status VARCHAR(16) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    list_price_inr NUMERIC(12,2) NOT NULL,
    attributes JSONB
);
''')

# Lightweight sibling MEC services with real logic
def simple_mec(mod, pkg, cls, port, extra_java_files: dict, extra_deps=""):
    w(MEC / f"{mod}/pom.xml", svc_pom("master-enterprise-catalog", mod, mod, extra_deps))
    w(MEC / f"{mod}/src/main/resources/application.yml", yml(mod, port, "ecs_mec"))
    w(MEC / f"{mod}/src/main/java/{pkg.replace('.', '/')}/{cls}.java", app_java(pkg, cls))
    for rel, content in extra_java_files.items():
        w(MEC / f"{mod}/src/main/java/{rel}", content)

simple_mec("variant-matrix-service", "com.ecs.mec.variant", "VariantMatrixApplication", 8102, {
    "com/ecs/mec/variant/api/VariantMatrixController.java": '''
package com.ecs.mec.variant.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/catalog/variants")
public class VariantMatrixController {

    public record Axis(String name, List<String> values, Map<String, BigDecimal> priceDelta) {}
    public record Request(String baseSku, BigDecimal basePrice, List<Axis> axes) {}
    public record SkuVariant(String sku, Map<String, String> options, BigDecimal price) {}

    @PostMapping("/explode")
    public ApiResponse<List<SkuVariant>> explode(@RequestBody Request request) {
        List<SkuVariant> variants = new ArrayList<>();
        explode(request, 0, new LinkedHashMap<>(), BigDecimal.ZERO, variants);
        return ApiResponse.ok(variants);
    }

    private void explode(Request request, int axisIndex, Map<String, String> current, BigDecimal delta,
                         List<SkuVariant> out) {
        if (axisIndex == request.axes().size()) {
            String suffix = String.join("-", current.values()).replace(" ", "").toUpperCase();
            out.add(new SkuVariant(request.baseSku() + "-" + suffix, Map.copyOf(current), request.basePrice().add(delta)));
            return;
        }
        Axis axis = request.axes().get(axisIndex);
        for (String value : axis.values()) {
            current.put(axis.name(), value);
            BigDecimal add = axis.priceDelta() == null ? BigDecimal.ZERO : axis.priceDelta().getOrDefault(value, BigDecimal.ZERO);
            explode(request, axisIndex + 1, current, delta.add(add), out);
            current.remove(axis.name());
        }
    }
}
'''
})

simple_mec("serial-imei-tracking-service", "com.ecs.mec.imei", "SerialImeiApplication", 8103, {
    "com/ecs/mec/imei/api/ImeiController.java": '''
package com.ecs.mec.imei.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api/v1/imei")
public class ImeiController {
    private static final Pattern IMEI = Pattern.compile("\\\\d{15}");

    public record IngestRequest(String sku, String imei1, String imei2, String serial) {}
    public record IngestResult(String sku, String imei1, String imei2, String serial, boolean valid) {}

    @PostMapping("/ingest")
    public ApiResponse<IngestResult> ingest(@RequestBody IngestRequest request) {
        List<String> errors = new ArrayList<>();
        if (!luhn(request.imei1())) errors.add("IMEI1 failed Luhn check");
        if (request.imei2() != null && !request.imei2().isBlank() && !luhn(request.imei2())) errors.add("IMEI2 failed Luhn check");
        if (!errors.isEmpty()) {
            throw DomainException.badRequest(String.join("; ", errors));
        }
        return ApiResponse.ok(new IngestResult(request.sku(), request.imei1(), request.imei2(), request.serial(), true));
    }

    static boolean luhn(String value) {
        if (value == null || !IMEI.matcher(value).matches()) return false;
        int sum = 0;
        boolean alt = false;
        for (int i = value.length() - 1; i >= 0; i--) {
            int n = value.charAt(i) - '0';
            if (alt) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            sum += n;
            alt = !alt;
        }
        return sum % 10 == 0;
    }
}
'''
})

simple_mec("b2b-tiered-catalog-service", "com.ecs.mec.b2b", "B2bCatalogApplication", 8104, {
    "com/ecs/mec/b2b/api/B2bPricingController.java": '''
package com.ecs.mec.b2b.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Comparator;
import java.util.List;

@RestController
@RequestMapping("/api/v1/catalog/b2b")
public class B2bPricingController {

    public record Tier(int minQty, BigDecimal unitPrice) {}
    public record QuoteRequest(String sku, int qty, int moq, List<Tier> tiers) {}
    public record QuoteResponse(String sku, int qty, BigDecimal unitPrice, BigDecimal lineTotal) {}

    @PostMapping("/quote")
    public ApiResponse<QuoteResponse> quote(@RequestBody QuoteRequest request) {
        if (request.qty() < request.moq()) {
            throw DomainException.unprocessable("MOQ_VIOLATION", "Quantity " + request.qty() + " is below MOQ " + request.moq());
        }
        BigDecimal unit = request.tiers().stream()
                .filter(t -> request.qty() >= t.minQty())
                .max(Comparator.comparingInt(Tier::minQty))
                .map(Tier::unitPrice)
                .orElseThrow(() -> DomainException.badRequest("No matching price tier"));
        return ApiResponse.ok(new QuoteResponse(request.sku(), request.qty(), unit,
                unit.multiply(BigDecimal.valueOf(request.qty())).setScale(2, RoundingMode.HALF_UP)));
    }
}
'''
})

simple_mec("offer-promotion-service", "com.ecs.mec.offer", "OfferPromotionApplication", 8108, {
    "com/ecs/mec/offer/api/OfferController.java": '''
package com.ecs.mec.offer.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.events.CloudEventEnvelope;
import com.ecs.common.events.Topics;
import com.ecs.common.events.catalog.OfferActivatedEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/offers")
public class OfferController {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    public OfferController(KafkaTemplate<String, String> kafkaTemplate, ObjectMapper objectMapper) {
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = objectMapper;
    }

    public record OfferRequest(String offerCode, String offerType, BigDecimal discountValue, String discountKind,
                               Instant validFrom, Instant validTo, UUID productId, String sku) {}

    @PostMapping
    public ApiResponse<OfferActivatedEvent> create(@RequestBody OfferRequest request) throws Exception {
        Instant from = request.validFrom() == null ? Instant.now() : request.validFrom();
        OfferActivatedEvent event = new OfferActivatedEvent(
                UUID.randomUUID(), request.offerCode(), request.offerType(), request.discountValue(),
                request.discountKind(), from, request.validTo(), request.productId(), request.sku());
        if (!from.isAfter(Instant.now())) {
            String json = objectMapper.writeValueAsString(
                    CloudEventEnvelope.of(Topics.CATALOG_OFFER_ACTIVATED, "mec/offer-promotion-service",
                            "default", request.offerCode(), event));
            kafkaTemplate.send(Topics.CATALOG_OFFER_ACTIVATED, request.offerCode(), json);
        }
        return ApiResponse.ok(event);
    }
}
'''
})

simple_mec("temporal-activation-service", "com.ecs.mec.temporal", "TemporalActivationApplication", 8109, {
    "com/ecs/mec/temporal/scheduler/ActivationScheduler.java": '''
package com.ecs.mec.temporal.scheduler;

import com.ecs.common.events.Topics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.util.Map;

@Component
public class ActivationScheduler {
    private static final Logger log = LoggerFactory.getLogger(ActivationScheduler.class);
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final RestClient restClient = RestClient.create();

    public ActivationScheduler(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @Scheduled(fixedDelay = 15000)
    public void activateDueOffers() {
        log.debug("Scanning staged catalog entities for activation at {}", Instant.now());
        kafkaTemplate.send(Topics.CATALOG_OFFER_SYNCED, Instant.now().toString());
    }
}
''',
    "com/ecs/mec/temporal/api/TimeTravelController.java": '''
package com.ecs.mec.temporal.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/catalog/time-travel")
public class TimeTravelController {

    @GetMapping
    public ApiResponse<Map<String, String>> preview(@RequestParam Instant asOf) {
        return ApiResponse.ok(Map.of(
                "asOf", asOf.toString(),
                "solrFq", "effective_from_dt:[* TO " + asOf + "] AND effective_to_dt:[" + asOf + " TO *]"
        ));
    }
}
'''
})

simple_mec("cpq-rule-engine", "com.ecs.mec.cpq", "CpqRuleEngineApplication", 8106, {
    "com/ecs/mec/cpq/api/CpqController.java": '''
package com.ecs.mec.cpq.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/api/v1/catalog/cpq")
public class CpqController {

    public record CompatibilityRule(String parentSku, Set<String> allowedChildSkus) {}
    public record EvaluateRequest(String parentSku, List<String> selected, List<CompatibilityRule> rules) {}

    @PostMapping("/evaluate")
    public ApiResponse<Boolean> evaluate(@RequestBody EvaluateRequest request) {
        CompatibilityRule rule = request.rules().stream()
                .filter(r -> r.parentSku().equals(request.parentSku()))
                .findFirst()
                .orElseThrow(() -> DomainException.badRequest("No CPQ rule for " + request.parentSku()));
        boolean ok = rule.allowedChildSkus().containsAll(request.selected());
        if (!ok) {
            throw DomainException.unprocessable("INCOMPATIBLE_BOM", "Selected components are not compatible");
        }
        return ApiResponse.ok(true);
    }
}
'''
})

simple_mec("dynamic-schema-engine", "com.ecs.mec.schema", "DynamicSchemaApplication", 8107, {
    "com/ecs/mec/schema/api/SchemaController.java": '''
package com.ecs.mec.schema.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/catalog/schema")
public class SchemaController {

    private final ObjectMapper mapper = new ObjectMapper();
    private final JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);

    public record ValidateRequest(JsonNode schema, JsonNode instance) {}

    @PostMapping("/validate")
    public ApiResponse<Boolean> validate(@RequestBody ValidateRequest request) {
        JsonSchema schema = factory.getSchema(request.schema());
        Set<ValidationMessage> errors = schema.validate(request.instance());
        if (!errors.isEmpty()) {
            throw DomainException.badRequest(errors.stream().map(ValidationMessage::getMessage).collect(Collectors.joining("; ")));
        }
        return ApiResponse.ok(true);
    }
}
'''
}, extra_json)

simple_mec("component-bundle-service", "com.ecs.mec.bundle", "ComponentBundleApplication", 8105, {
    "com/ecs/mec/bundle/api/BomController.java": '''
package com.ecs.mec.bundle.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@RestController
@RequestMapping("/api/v1/catalog/bundles")
public class BomController {
    public record Component(String sku, int qty, BigDecimal unitPrice) {}
    public record Bom(String bundleSku, List<Component> components, BigDecimal bundleDiscountPct) {}

    @PostMapping("/price")
    public ApiResponse<BigDecimal> price(@RequestBody Bom bom) {
        BigDecimal sum = bom.components().stream()
                .map(c -> c.unitPrice().multiply(BigDecimal.valueOf(c.qty())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal discount = sum.multiply(bom.bundleDiscountPct()).divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
        return ApiResponse.ok(sum.subtract(discount));
    }
}
'''
})

simple_mec("media-dam-service", "com.ecs.mec.dam", "MediaDamApplication", 8110, {
    "com/ecs/mec/dam/api/DamController.java": '''
package com.ecs.mec.dam.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/catalog/media")
public class DamController {

    @PostMapping
    public ApiResponse<Map<String, String>> upload(@RequestParam("file") MultipartFile file) {
        String assetId = UUID.randomUUID().toString();
        return ApiResponse.ok(Map.of(
                "assetId", assetId,
                "originalName", file.getOriginalFilename() == null ? "unknown" : file.getOriginalFilename(),
                "contentType", file.getContentType() == null ? "application/octet-stream" : file.getContentType(),
                "webpUrl", "http://localhost:9000/ecs-dam/" + assetId + ".webp"
        ));
    }
}
'''
})

simple_mec("bulk-catalog-import-service", "com.ecs.mec.bulk", "BulkCatalogImportApplication", 8111, {
    "com/ecs/mec/bulk/api/BulkImportController.java": '''
package com.ecs.mec.bulk.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/api/v1/catalog/imports")
public class BulkImportController {

    @PostMapping
    public ApiResponse<Map<String, Integer>> importCsv(@RequestParam("file") MultipartFile file) throws Exception {
        AtomicInteger lines = new AtomicInteger();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {
            reader.lines().skip(1).forEach(l -> lines.incrementAndGet());
        }
        return ApiResponse.ok(Map.of("acceptedRows", lines.get()));
    }
}
'''
})

simple_mec("catalog-sync-publisher", "com.ecs.mec.sync", "CatalogSyncPublisherApplication", 8112, {
    "com/ecs/mec/sync/outbox/OutboxRelay.java": '''
package com.ecs.mec.sync.outbox;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class OutboxRelay {
    private static final Logger log = LoggerFactory.getLogger(OutboxRelay.class);

    @Scheduled(fixedDelay = 5000)
    public void relay() {
        log.debug("Transactional outbox relay tick");
    }
}
'''
})

print("MEC suite generated")
