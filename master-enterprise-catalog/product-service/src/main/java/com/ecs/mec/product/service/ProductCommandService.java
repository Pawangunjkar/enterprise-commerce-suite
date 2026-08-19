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
