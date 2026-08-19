package com.ecs.saga;

import com.ecs.common.core.exception.DomainException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

public class SagaOrchestrator<C> {
    private static final Logger log = LoggerFactory.getLogger(SagaOrchestrator.class);
    private final List<SagaStep<C>> steps;

    public SagaOrchestrator(List<SagaStep<C>> steps) {
        this.steps = List.copyOf(steps);
    }

    public CheckoutSagaState run(C context) {
        List<SagaStep<C>> executed = new ArrayList<>();
        try {
            CheckoutSagaState last = CheckoutSagaState.CART_VALIDATED;
            for (SagaStep<C> step : steps) {
                log.info("Executing saga step {}", step.name());
                last = step.execute(context);
                executed.add(step);
            }
            return last == CheckoutSagaState.PAYMENT_CAPTURED ? CheckoutSagaState.COMPLETED : last;
        } catch (Exception ex) {
            log.error("Saga failed, compensating {} steps", executed.size(), ex);
            for (int i = executed.size() - 1; i >= 0; i--) {
                try {
                    executed.get(i).compensate(context);
                } catch (Exception compensateEx) {
                    log.error("Compensation failed for {}", executed.get(i).name(), compensateEx);
                }
            }
            throw DomainException.unprocessable("SAGA_FAILED", ex.getMessage());
        }
    }
}
