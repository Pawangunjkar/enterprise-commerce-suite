package com.ecs.oms.catalogreplica.listener;

import com.ecs.common.events.Topics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class ReplicaListener {
    private static final Logger log = LoggerFactory.getLogger(ReplicaListener.class);
    private final StringRedisTemplate redis;
    public ReplicaListener(StringRedisTemplate redis) { this.redis = redis; }

    @KafkaListener(topics = Topics.CATALOG_PRODUCT_PUBLISHED)
    public void onProduct(String payload) {
        redis.opsForValue().set("catalog:last-event", payload);
        log.info("Updated local catalog replica");
    }
}
