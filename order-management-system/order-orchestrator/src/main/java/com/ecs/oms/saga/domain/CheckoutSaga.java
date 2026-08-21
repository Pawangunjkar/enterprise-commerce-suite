package com.ecs.oms.saga.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "checkout_saga")
public class CheckoutSaga extends BaseEntity {

    @Column(nullable = false)
    private UUID orderId;

    @Column(nullable = false, length = 32)
    private String state;

    @Column(length = 64)
    private String lastStep;

    @Column(columnDefinition = "text")
    private String errorMessage;

    public UUID getOrderId() { return orderId; }
    public void setOrderId(UUID orderId) { this.orderId = orderId; }
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    public String getLastStep() { return lastStep; }
    public void setLastStep(String lastStep) { this.lastStep = lastStep; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
}
