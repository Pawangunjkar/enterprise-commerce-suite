#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PI = ROOT / "platform-infrastructure"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


BOOT = open(ROOT / "tools/_gen_infra_svc.py", encoding="utf-8").read()
# reuse pom template inline
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


def yml(app, port, db, extra=""):
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
  flyway:
    enabled: true
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: {app}
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
{extra}
'''


# MCA audit
w(PI / "mca-audit-trail-service/pom.xml", svc_pom("mca-audit-trail-service", "MCA Audit Trail Service"))
w(PI / "mca-audit-trail-service/src/main/resources/application.yml", yml("mca-audit-trail-service", 8093, "ecs_platform"))
w(PI / "mca-audit-trail-service/src/main/java/com/ecs/audit/McaAuditTrailApplication.java", '''
package com.ecs.audit;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class McaAuditTrailApplication {
    public static void main(String[] args) {
        SpringApplication.run(McaAuditTrailApplication.class, args);
    }
}
''')

w(PI / "mca-audit-trail-service/src/main/java/com/ecs/audit/domain/AuditRecord.java", '''
package com.ecs.audit.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(name = "mca_audit_log")
public class AuditRecord {
    @Id
    private UUID id = UUID.randomUUID();

    @Column(nullable = false)
    private Instant occurredAt = Instant.now();

    @Column(nullable = false, length = 64)
    private String tenantId;

    @Column(nullable = false, length = 128)
    private String actor;

    @Column(nullable = false, length = 64)
    private String action;

    @Column(nullable = false, length = 128)
    private String resourceType;

    @Column(nullable = false, length = 128)
    private String resourceId;

    @Column(nullable = false, length = 64)
    private String checksum;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb", nullable = false)
    private Map<String, Object> payload;

    public UUID getId() { return id; }
    public Instant getOccurredAt() { return occurredAt; }
    public String getTenantId() { return tenantId; }
    public void setTenantId(String tenantId) { this.tenantId = tenantId; }
    public String getActor() { return actor; }
    public void setActor(String actor) { this.actor = actor; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getResourceType() { return resourceType; }
    public void setResourceType(String resourceType) { this.resourceType = resourceType; }
    public String getResourceId() { return resourceId; }
    public void setResourceId(String resourceId) { this.resourceId = resourceId; }
    public String getChecksum() { return checksum; }
    public void setChecksum(String checksum) { this.checksum = checksum; }
    public Map<String, Object> getPayload() { return payload; }
    public void setPayload(Map<String, Object> payload) { this.payload = payload; }
}
''')

w(PI / "mca-audit-trail-service/src/main/java/com/ecs/audit/repo/AuditRecordRepository.java", '''
package com.ecs.audit.repo;

import com.ecs.audit.domain.AuditRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface AuditRecordRepository extends JpaRepository<AuditRecord, UUID> {
    Page<AuditRecord> findByTenantIdAndResourceType(String tenantId, String resourceType, Pageable pageable);
}
''')

w(PI / "mca-audit-trail-service/src/main/java/com/ecs/audit/api/AuditController.java", '''
package com.ecs.audit.api;

import com.ecs.audit.domain.AuditRecord;
import com.ecs.audit.repo.AuditRecordRepository;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.tenant.TenantContext;
import jakarta.validation.constraints.NotBlank;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/audit")
public class AuditController {

    private final AuditRecordRepository repository;

    public AuditController(AuditRecordRepository repository) {
        this.repository = repository;
    }

    public record AppendRequest(
            @NotBlank String actor,
            @NotBlank String action,
            @NotBlank String resourceType,
            @NotBlank String resourceId,
            Map<String, Object> payload
    ) {}

    @PostMapping
    public ApiResponse<AuditRecord> append(@RequestBody AppendRequest request) {
        AuditRecord record = new AuditRecord();
        record.setTenantId(TenantContext.get());
        record.setActor(request.actor());
        record.setAction(request.action());
        record.setResourceType(request.resourceType());
        record.setResourceId(request.resourceId());
        record.setPayload(request.payload() == null ? Map.of() : request.payload());
        String raw = record.getTenantId() + "|" + record.getActor() + "|" + record.getAction()
                + "|" + record.getResourceType() + "|" + record.getResourceId() + "|" + record.getOccurredAt();
        record.setChecksum(sha256(raw));
        return ApiResponse.ok(repository.save(record));
    }

    @GetMapping
    public ApiResponse<PageResponse<AuditRecord>> list(
            @RequestParam String resourceType,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size
    ) {
        return ApiResponse.ok(PageResponse.from(
                repository.findByTenantIdAndResourceType(TenantContext.get(), resourceType, PageRequest.of(page, size))));
    }

    private static String sha256(String raw) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(raw.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
    }
}
''')

w(PI / "mca-audit-trail-service/src/main/resources/db/migration/V1__audit.sql", '''
CREATE TABLE IF NOT EXISTS mca_audit_log (
    id UUID PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(128) NOT NULL,
    resource_id VARCHAR(128) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_type ON mca_audit_log (tenant_id, resource_type, occurred_at DESC);
REVOKE UPDATE, DELETE ON mca_audit_log FROM PUBLIC;
''')

# DLQ
w(PI / "kafka-dlq-manager/pom.xml", svc_pom("kafka-dlq-manager", "Kafka DLQ Manager"))
w(PI / "kafka-dlq-manager/src/main/resources/application.yml", yml("kafka-dlq-manager", 8092, "ecs_platform"))
w(PI / "kafka-dlq-manager/src/main/java/com/ecs/dlq/KafkaDlqManagerApplication.java", '''
package com.ecs.dlq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class KafkaDlqManagerApplication {
    public static void main(String[] args) {
        SpringApplication.run(KafkaDlqManagerApplication.class, args);
    }
}
''')

w(PI / "kafka-dlq-manager/src/main/java/com/ecs/dlq/domain/DeadLetter.java", '''
package com.ecs.dlq.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "dead_letter")
public class DeadLetter extends BaseEntity {

    @Column(nullable = false)
    private String originalTopic;

    @Column(nullable = false)
    private String consumerGroup;

    @Column(nullable = false, columnDefinition = "text")
    private String payload;

    @Column(nullable = false, columnDefinition = "text")
    private String errorMessage;

    @Column(nullable = false)
    private int replayAttempts;

    @Column(nullable = false, length = 24)
    private String status = "OPEN";

    public String getOriginalTopic() { return originalTopic; }
    public void setOriginalTopic(String originalTopic) { this.originalTopic = originalTopic; }
    public String getConsumerGroup() { return consumerGroup; }
    public void setConsumerGroup(String consumerGroup) { this.consumerGroup = consumerGroup; }
    public String getPayload() { return payload; }
    public void setPayload(String payload) { this.payload = payload; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public int getReplayAttempts() { return replayAttempts; }
    public void setReplayAttempts(int replayAttempts) { this.replayAttempts = replayAttempts; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
''')

w(PI / "kafka-dlq-manager/src/main/java/com/ecs/dlq/repo/DeadLetterRepository.java", '''
package com.ecs.dlq.repo;

import com.ecs.dlq.domain.DeadLetter;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface DeadLetterRepository extends JpaRepository<DeadLetter, UUID> {
    Page<DeadLetter> findByStatus(String status, Pageable pageable);
}
''')

w(PI / "kafka-dlq-manager/src/main/java/com/ecs/dlq/api/DlqController.java", '''
package com.ecs.dlq.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.dlq.domain.DeadLetter;
import com.ecs.dlq.repo.DeadLetterRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/dlq")
public class DlqController {

    private final DeadLetterRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    public DlqController(DeadLetterRepository repository, KafkaTemplate<String, String> kafkaTemplate) {
        this.repository = repository;
        this.kafkaTemplate = kafkaTemplate;
    }

    @GetMapping
    public ApiResponse<PageResponse<DeadLetter>> list(
            @RequestParam(defaultValue = "OPEN") String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ApiResponse.ok(PageResponse.from(repository.findByStatus(status, PageRequest.of(page, size))));
    }

    @PostMapping("/{id}/replay")
    public ApiResponse<DeadLetter> replay(@PathVariable UUID id) {
        DeadLetter letter = repository.findById(id).orElseThrow(() -> DomainException.notFound("DeadLetter", id));
        kafkaTemplate.send(letter.getOriginalTopic(), letter.getPayload());
        letter.setReplayAttempts(letter.getReplayAttempts() + 1);
        letter.setStatus("REPLAYED");
        return ApiResponse.ok(repository.save(letter), "Message replayed to " + letter.getOriginalTopic());
    }

    @PostMapping("/replay")
    public ApiResponse<DeadLetter> replayAlias(@RequestParam UUID id) {
        return replay(id);
    }
}
''')

w(PI / "kafka-dlq-manager/src/main/java/com/ecs/dlq/listener/DlqCaptureListener.java", '''
package com.ecs.dlq.listener;

import com.ecs.common.events.Topics;
import com.ecs.dlq.domain.DeadLetter;
import com.ecs.dlq.repo.DeadLetterRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.stereotype.Component;

@Component
public class DlqCaptureListener {

    private final DeadLetterRepository repository;

    public DlqCaptureListener(DeadLetterRepository repository) {
        this.repository = repository;
    }

    @KafkaListener(topics = Topics.DLQ)
    public void onPoison(String payload,
                         @Header(name = "original-topic", required = false) String topic,
                         @Header(name = "kafka_receivedGroupId", required = false) String group,
                         @Header(name = "error-message", required = false) String error) {
        DeadLetter letter = new DeadLetter();
        letter.setOriginalTopic(topic == null ? "unknown" : topic);
        letter.setConsumerGroup(group == null ? "unknown" : group);
        letter.setPayload(payload);
        letter.setErrorMessage(error == null ? "unspecified" : error);
        repository.save(letter);
    }
}
''')

w(PI / "kafka-dlq-manager/src/main/resources/db/migration/V1__dlq.sql", '''
CREATE TABLE IF NOT EXISTS dead_letter (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    original_topic VARCHAR(255) NOT NULL,
    consumer_group VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    error_message TEXT NOT NULL,
    replay_attempts INT NOT NULL DEFAULT 0,
    status VARCHAR(24) NOT NULL
);
''')

# Notification
w(PI / "notification-service/pom.xml", svc_pom("notification-service", "Notification Service", '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webflux</artifactId>
        </dependency>
'''))
w(PI / "notification-service/src/main/resources/application.yml", yml("notification-service", 8094, "ecs_platform", '''
ecs:
  notify:
    gupshup:
      base-url: https://api.gupshup.io
      api-key: ${GUPSHUP_API_KEY:dev-key}
    msg91:
      base-url: https://api.msg91.com
      auth-key: ${MSG91_AUTH_KEY:dev-key}
'''))
w(PI / "notification-service/src/main/java/com/ecs/notify/NotificationServiceApplication.java", '''
package com.ecs.notify;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class NotificationServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(NotificationServiceApplication.class, args);
    }
}
''')

w(PI / "notification-service/src/main/java/com/ecs/notify/api/NotificationController.java", '''
package com.ecs.notify.api;

import com.ecs.common.core.api.ApiResponse;
import jakarta.validation.constraints.NotBlank;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/notifications")
public class NotificationController {
    private static final Logger log = LoggerFactory.getLogger(NotificationController.class);

    public record NotifyRequest(
            @NotBlank String channel,
            @NotBlank String to,
            @NotBlank String template,
            Map<String, String> params
    ) {}

    @PostMapping
    public ApiResponse<Map<String, String>> send(@RequestBody NotifyRequest request) {
        String messageId = UUID.randomUUID().toString();
        log.info("Dispatching {} to {} template={} id={}", request.channel(), request.to(), request.template(), messageId);
        return ApiResponse.ok(Map.of(
                "messageId", messageId,
                "channel", request.channel(),
                "status", "QUEUED"
        ));
    }
}
''')

# Solr indexer
w(PI / "search-solr-indexer/pom.xml", svc_pom("search-solr-indexer", "Search Solr Indexer", '''
        <dependency>
            <groupId>org.apache.solr</groupId>
            <artifactId>solr-solrj</artifactId>
            <version>9.7.0</version>
        </dependency>
'''))
w(PI / "search-solr-indexer/src/main/resources/application.yml", yml("search-solr-indexer", 8090, "ecs_platform", '''
ecs:
  solr:
    zk-host: localhost:2181
    collection: products
    base-url: http://localhost:8983/solr
'''))
w(PI / "search-solr-indexer/src/main/java/com/ecs/search/SearchSolrIndexerApplication.java", '''
package com.ecs.search;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class SearchSolrIndexerApplication {
    public static void main(String[] args) {
        SpringApplication.run(SearchSolrIndexerApplication.class, args);
    }
}
''')

w(PI / "search-solr-indexer/src/main/java/com/ecs/search/config/SolrConfig.java", '''
package com.ecs.search.config;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.impl.Http2SolrClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SolrConfig {

    @Bean
    public SolrClient solrClient(@Value("${ecs.solr.base-url}") String baseUrl) {
        return new Http2SolrClient.Builder(baseUrl).build();
    }
}
''')

w(PI / "search-solr-indexer/src/main/java/com/ecs/search/index/CatalogIndexListener.java", '''
package com.ecs.search.index;

import com.ecs.common.events.Topics;
import com.ecs.common.events.catalog.ProductPublishedEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.common.SolrInputDocument;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class CatalogIndexListener {

    private final SolrClient solrClient;
    private final ObjectMapper objectMapper;
    private final String collection;

    public CatalogIndexListener(SolrClient solrClient, ObjectMapper objectMapper,
                                @Value("${ecs.solr.collection}") String collection) {
        this.solrClient = solrClient;
        this.objectMapper = objectMapper;
        this.collection = collection;
    }

    @KafkaListener(topics = {Topics.CATALOG_PRODUCT_PUBLISHED, Topics.CATALOG_PRODUCT_ACTIVATED})
    public void onProduct(String json) throws Exception {
        ProductPublishedEvent event = objectMapper.readValue(json, ProductPublishedEvent.class);
        SolrInputDocument doc = new SolrInputDocument();
        doc.addField("id", event.productId().toString());
        doc.addField("sku_s", event.sku());
        doc.addField("name_txt_en", event.name());
        doc.addField("name_txt_hi", event.name());
        doc.addField("brand_s", event.brand());
        doc.addField("category_path_s", event.categoryPath());
        doc.addField("hsn_s", event.hsnCode());
        doc.addField("status_s", event.status());
        doc.addField("list_price_f", event.listPriceInr());
        doc.addField("effective_from_dt", event.effectiveFrom() == null ? Instant.now().toString() : event.effectiveFrom().toString());
        doc.addField("effective_to_dt", event.effectiveTo() == null ? "2099-12-31T23:59:59Z" : event.effectiveTo().toString());
        if (event.attributes() != null) {
            event.attributes().forEach((k, v) -> {
                if (v instanceof Number n) {
                    if (n instanceof Double || n instanceof Float) {
                        doc.addField("attr_" + k + "_f", n);
                    } else {
                        doc.addField("attr_" + k + "_i", n);
                    }
                } else {
                    doc.addField("attr_" + k + "_s", String.valueOf(v));
                }
            });
        }
        solrClient.add(collection, doc);
        solrClient.commit(collection);
    }
}
''')

w(PI / "search-solr-indexer/src/main/java/com/ecs/search/api/ProductSearchController.java", '''
package com.ecs.search.api;

import com.ecs.common.core.api.ApiResponse;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/search")
public class ProductSearchController {

    private final SolrClient solrClient;
    private final String collection;

    public ProductSearchController(SolrClient solrClient, @Value("${ecs.solr.collection}") String collection) {
        this.solrClient = solrClient;
        this.collection = collection;
    }

    @GetMapping("/products")
    public ApiResponse<Map<String, Object>> search(
            @RequestParam(defaultValue = "*:*") String q,
            @RequestParam(required = false) String brand,
            @RequestParam(required = false) Integer ram,
            @RequestParam(required = false) String color,
            @RequestParam(required = false) Double minPrice,
            @RequestParam(required = false) Double maxPrice,
            @RequestParam(defaultValue = "0") int start,
            @RequestParam(defaultValue = "24") int rows
    ) throws Exception {
        SolrQuery query = new SolrQuery(q);
        query.setStart(start);
        query.setRows(rows);
        query.addFilterQuery("status_s:ACTIVE");
        String now = Instant.now().toString();
        query.addFilterQuery("effective_from_dt:[* TO " + now + "]");
        query.addFilterQuery("effective_to_dt:[" + now + " TO *]");
        if (brand != null) query.addFilterQuery("brand_s:" + brand);
        if (ram != null) query.addFilterQuery("attr_ram_i:" + ram);
        if (color != null) query.addFilterQuery("attr_color_s:" + color);
        if (minPrice != null || maxPrice != null) {
            String lo = minPrice == null ? "*" : minPrice.toString();
            String hi = maxPrice == null ? "*" : maxPrice.toString();
            query.addFilterQuery("list_price_f:[" + lo + " TO " + hi + "]");
        }
        query.setFacet(true);
        query.addFacetField("brand_s", "attr_ram_i", "attr_color_s", "attr_storage_s");
        query.set("defType", "edismax");
        query.set("qf", "name_txt_en name_txt_hi sku_s brand_s");
        QueryResponse response = solrClient.query(collection, query);
        List<Map<String, Object>> docs = response.getResults().stream().map(this::toMap).toList();
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("numFound", response.getResults().getNumFound());
        body.put("docs", docs);
        body.put("facets", response.getFacetFields());
        return ApiResponse.ok(body);
    }

    @GetMapping("/autocomplete")
    public ApiResponse<List<String>> autocomplete(@RequestParam String q) throws Exception {
        SolrQuery query = new SolrQuery(q + "*");
        query.setRows(8);
        query.set("defType", "edismax");
        query.set("qf", "name_txt_en name_txt_hi");
        query.setFields("name_txt_en");
        QueryResponse response = solrClient.query(collection, query);
        return ApiResponse.ok(response.getResults().stream()
                .map(d -> String.valueOf(d.getFieldValue("name_txt_en")))
                .toList());
    }

    private Map<String, Object> toMap(SolrDocument document) {
        Map<String, Object> map = new LinkedHashMap<>();
        document.forEach(map::put);
        return map;
    }
}
''')

# Keycloak realm
w(PI / "auth-server-keycloak/ecs-realm.json", '''
{
  "realm": "ecs",
  "enabled": true,
  "sslRequired": "external",
  "roles": {
    "realm": [
      {"name": "SUPER_ADMIN"},
      {"name": "CATALOG_ADMIN"},
      {"name": "OMS_ADMIN"},
      {"name": "BILLING_ADMIN"},
      {"name": "CRM_ADMIN"},
      {"name": "BUYER"}
    ]
  },
  "clients": [
    {
      "clientId": "ecs-gateway",
      "publicClient": false,
      "secret": "ecs-gateway-secret",
      "directAccessGrantsEnabled": true,
      "standardFlowEnabled": true,
      "redirectUris": ["http://localhost:5173/*", "http://localhost:5174/*", "http://localhost:8080/*"],
      "webOrigins": ["+"]
    },
    {
      "clientId": "ecs-storefront",
      "publicClient": true,
      "directAccessGrantsEnabled": true,
      "standardFlowEnabled": true,
      "redirectUris": ["http://localhost:5173/*"],
      "webOrigins": ["+"]
    }
  ]
}
''')

print("remaining infra services written")
