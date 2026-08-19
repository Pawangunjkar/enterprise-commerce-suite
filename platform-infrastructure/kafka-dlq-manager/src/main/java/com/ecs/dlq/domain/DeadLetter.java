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
