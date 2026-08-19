package com.ecs.saga;

public interface SagaStep<C> {
    String name();
    CheckoutSagaState execute(C context);
    void compensate(C context);
}
