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
