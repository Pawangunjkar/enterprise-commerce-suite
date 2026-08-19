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
