package com.ecs.oms.saga.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.saga.CheckoutSagaState;
import com.ecs.saga.SagaOrchestrator;
import com.ecs.saga.SagaStep;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderSagaController {

    public record PlaceOrderRequest(String cartId, String pincode, String paymentMode, BigDecimal amount) {}
    public static final class Ctx {
        public final PlaceOrderRequest request;
        public final AtomicReference<UUID> orderId = new AtomicReference<>(UUID.randomUUID());
        public Ctx(PlaceOrderRequest request) { this.request = request; }
    }

    @PostMapping
    public ApiResponse<CheckoutSagaState> place(@RequestBody PlaceOrderRequest request) {
        SagaOrchestrator<Ctx> orchestrator = new SagaOrchestrator<>(List.of(
                step("atp-lock", CheckoutSagaState.ATP_LOCKED),
                step("payment-or-cod", "COD".equalsIgnoreCase(request.paymentMode())
                        ? CheckoutSagaState.COD_VERIFIED : CheckoutSagaState.PAYMENT_AUTHORIZED),
                step("warehouse-route", CheckoutSagaState.WAREHOUSE_ROUTED),
                step("capture-on-dispatch", CheckoutSagaState.PAYMENT_CAPTURED)
        ));
        return ApiResponse.ok(orchestrator.run(new Ctx(request)));
    }

    private SagaStep<Ctx> step(String name, CheckoutSagaState state) {
        return new SagaStep<>() {
            public String name() { return name; }
            public CheckoutSagaState execute(Ctx context) { return state; }
            public void compensate(Ctx context) { }
        };
    }
}
