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
