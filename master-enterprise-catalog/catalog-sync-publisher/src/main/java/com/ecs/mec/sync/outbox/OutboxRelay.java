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
