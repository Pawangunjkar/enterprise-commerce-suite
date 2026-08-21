package com.ecs.oms.saga.service;

import com.ecs.common.core.exception.DomainException;
import com.ecs.common.core.http.DownstreamClient;
import com.ecs.oms.saga.api.OrderSagaController.LineRequest;
import com.ecs.oms.saga.api.OrderSagaController.PlaceOrderRequest;
import com.ecs.oms.saga.domain.CheckoutSaga;
import com.ecs.oms.saga.domain.CommerceOrder;
import com.ecs.oms.saga.domain.OrderLine;
import com.ecs.oms.saga.repo.CheckoutSagaRepository;
import com.ecs.oms.saga.repo.CommerceOrderRepository;
import com.ecs.saga.CheckoutSagaState;
import com.ecs.saga.SagaOrchestrator;
import com.ecs.saga.SagaStep;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Year;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

@Service
public class CheckoutSagaService {

    private final CommerceOrderRepository orders;
    private final CheckoutSagaRepository sagas;
    private final DownstreamClient downstream;
    private final String atpUrl;
    private final String paymentUrl;
    private final String wmsUrl;
    private final String invoiceUrl;

    public CheckoutSagaService(
            CommerceOrderRepository orders,
            CheckoutSagaRepository sagas,
            DownstreamClient downstream,
            @Value("${ecs.downstream.atp-url}") String atpUrl,
            @Value("${ecs.downstream.payment-url}") String paymentUrl,
            @Value("${ecs.downstream.wms-url}") String wmsUrl,
            @Value("${ecs.downstream.invoice-url}") String invoiceUrl
    ) {
        this.orders = orders;
        this.sagas = sagas;
        this.downstream = downstream;
        this.atpUrl = atpUrl;
        this.paymentUrl = paymentUrl;
        this.wmsUrl = wmsUrl;
        this.invoiceUrl = invoiceUrl;
    }

    public record PlaceOrderResult(CommerceOrder order, CheckoutSagaState state) {}

    public static final class Ctx {
        private final PlaceOrderRequest request;
        private CommerceOrder order;
        private CheckoutSaga saga;
        private boolean atpLocked;
        private UUID paymentId;
        private String waveId;

        public Ctx(PlaceOrderRequest request) {
            this.request = request;
        }
    }

    public PlaceOrderResult place(PlaceOrderRequest request) {
        Ctx ctx = new Ctx(normalize(request));
        persistDraft(ctx);
        try {
            CheckoutSagaState state = new SagaOrchestrator<>(List.of(
                    step("atp-lock", this::lockAtp, this::unlockAtp),
                    step("payment-or-cod", this::authorizePayment, this::voidPayment),
                    step("warehouse-route", this::routeWarehouse, this::cancelWave),
                    step("capture-on-dispatch", this::captureAndInvoice, ctx2 -> {})
            )).run(ctx);
            touch(ctx, state, "completed", null);
            ctx.order.setStatus(CheckoutSagaState.COMPLETED.name());
            orders.save(ctx.order);
            return new PlaceOrderResult(ctx.order, CheckoutSagaState.COMPLETED);
        } catch (RuntimeException ex) {
            touch(ctx, CheckoutSagaState.FAILED, "failed", ex.getMessage());
            if (ctx.order != null) {
                ctx.order.setStatus(CheckoutSagaState.FAILED.name());
                orders.save(ctx.order);
            }
            throw ex;
        }
    }

    public CommerceOrder get(UUID id) {
        return orders.findById(id).orElseThrow(() -> DomainException.notFound("order", id));
    }

    private PlaceOrderRequest normalize(PlaceOrderRequest request) {
        List<LineRequest> lines = request.lines();
        if (lines == null || lines.isEmpty()) {
            BigDecimal amount = request.amount() == null ? new BigDecimal("49999.00") : request.amount();
            lines = List.of(new LineRequest("SKU-PHONE-8-128-BLACK", 1, amount, "8517"));
        }
        String mode = request.paymentMode() == null ? "UPI" : request.paymentMode();
        String pincode = request.pincode() == null ? "110001" : request.pincode();
        String cartId = request.cartId() == null ? "CART-" + UUID.randomUUID() : request.cartId();
        BigDecimal amount = request.amount();
        if (amount == null) {
            amount = lines.stream()
                    .map(l -> l.unitPriceInr().multiply(BigDecimal.valueOf(l.qty())))
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
        }
        return new PlaceOrderRequest(
                cartId,
                pincode,
                mode,
                amount,
                request.customerId(),
                request.originState() == null ? "HR" : request.originState(),
                request.destState() == null ? "DL" : request.destState(),
                lines
        );
    }

    private void persistDraft(Ctx ctx) {
        CommerceOrder order = new CommerceOrder();
        order.setOrderNumber("ECS-" + Year.now().getValue() + "-" + ThreadLocalRandom.current().nextInt(100000, 999999));
        order.setCartId(ctx.request.cartId());
        order.setCustomerId(ctx.request.customerId());
        order.setPincode(ctx.request.pincode());
        order.setPaymentMode(ctx.request.paymentMode());
        order.setStatus(CheckoutSagaState.CART_VALIDATED.name());
        order.setGrandTotalInr(ctx.request.amount());
        order.setOriginState(ctx.request.originState());
        order.setDestState(ctx.request.destState());
        for (LineRequest line : ctx.request.lines()) {
            OrderLine entity = new OrderLine();
            entity.setSku(line.sku());
            entity.setQty(line.qty());
            entity.setUnitPriceInr(line.unitPriceInr());
            entity.setHsnCode(line.hsnCode());
            order.addLine(entity);
        }
        ctx.order = orders.save(order);
        CheckoutSaga saga = new CheckoutSaga();
        saga.setOrderId(order.getId());
        saga.setState(CheckoutSagaState.CART_VALIDATED.name());
        saga.setLastStep("persist-order");
        ctx.saga = sagas.save(saga);
    }

    private CheckoutSagaState lockAtp(Ctx ctx) {
        for (OrderLine line : ctx.order.getLines()) {
            downstream.postUrl(atpUrl + "/api/v1/inventory/lock", Map.of(
                    "sku", line.getSku(),
                    "qty", line.getQty(),
                    "warehouse", "NDC-HR"
            ));
        }
        ctx.atpLocked = true;
        touch(ctx, CheckoutSagaState.ATP_LOCKED, "atp-lock", null);
        ctx.order.setStatus(CheckoutSagaState.ATP_LOCKED.name());
        orders.save(ctx.order);
        return CheckoutSagaState.ATP_LOCKED;
    }

    private void unlockAtp(Ctx ctx) {
        if (!ctx.atpLocked) {
            return;
        }
        for (OrderLine line : ctx.order.getLines()) {
            try {
                downstream.postUrl(atpUrl + "/api/v1/inventory/unlock", Map.of(
                        "sku", line.getSku(),
                        "qty", line.getQty()
                ));
            } catch (Exception ignored) {
                // compensation is best-effort
            }
        }
    }

    private CheckoutSagaState authorizePayment(Ctx ctx) {
        if ("COD".equalsIgnoreCase(ctx.request.paymentMode())) {
            touch(ctx, CheckoutSagaState.COD_VERIFIED, "payment-or-cod", null);
            ctx.order.setStatus(CheckoutSagaState.COD_VERIFIED.name());
            orders.save(ctx.order);
            return CheckoutSagaState.COD_VERIFIED;
        }
        Map<String, Object> data = downstream.postUrl(paymentUrl + "/api/v1/payments/authorize", Map.of(
                "orderId", ctx.order.getId().toString(),
                "amount", ctx.order.getGrandTotalInr(),
                "mode", ctx.request.paymentMode()
        ));
        ctx.paymentId = UUID.fromString(String.valueOf(data.get("paymentId")));
        ctx.order.setPaymentId(ctx.paymentId);
        touch(ctx, CheckoutSagaState.PAYMENT_AUTHORIZED, "payment-or-cod", null);
        ctx.order.setStatus(CheckoutSagaState.PAYMENT_AUTHORIZED.name());
        orders.save(ctx.order);
        return CheckoutSagaState.PAYMENT_AUTHORIZED;
    }

    private void voidPayment(Ctx ctx) {
        if (ctx.paymentId == null) {
            return;
        }
        try {
            downstream.postUrl(paymentUrl + "/api/v1/payments/" + ctx.paymentId + "/void", Map.of());
        } catch (Exception ignored) {
            // compensation is best-effort
        }
    }

    private CheckoutSagaState routeWarehouse(Ctx ctx) {
        List<Map<String, Object>> pickLines = ctx.order.getLines().stream()
                .map(line -> Map.<String, Object>of(
                        "sku", line.getSku(),
                        "bin", "A-01-01",
                        "qty", line.getQty()
                ))
                .toList();
        Map<String, Object> data = downstream.postUrl(wmsUrl + "/api/v1/wms/waves", pickLines);
        ctx.waveId = String.valueOf(data.get("waveId"));
        ctx.order.setWaveId(ctx.waveId);
        touch(ctx, CheckoutSagaState.WAREHOUSE_ROUTED, "warehouse-route", null);
        ctx.order.setStatus(CheckoutSagaState.WAREHOUSE_ROUTED.name());
        orders.save(ctx.order);
        return CheckoutSagaState.WAREHOUSE_ROUTED;
    }

    private void cancelWave(Ctx ctx) {
        if (ctx.waveId == null) {
            return;
        }
        try {
            downstream.postUrl(wmsUrl + "/api/v1/wms/waves/" + ctx.waveId + "/cancel", Map.of());
        } catch (Exception ignored) {
            // compensation is best-effort
        }
    }

    private CheckoutSagaState captureAndInvoice(Ctx ctx) {
        if (ctx.paymentId != null) {
            downstream.postUrl(paymentUrl + "/api/v1/payments/" + ctx.paymentId + "/capture", Map.of());
        }
        Map<String, Object> invoice = downstream.postUrl(invoiceUrl + "/api/v1/invoices", Map.of(
                "orderId", ctx.order.getId().toString(),
                "orderNumber", ctx.order.getOrderNumber(),
                "taxable", ctx.order.getGrandTotalInr(),
                "slab", 18,
                "originState", ctx.order.getOriginState(),
                "destState", ctx.order.getDestState(),
                "hsn", ctx.order.getLines().isEmpty() ? "8517" : ctx.order.getLines().getFirst().getHsnCode()
        ));
        Object invoiceId = invoice.get("invoiceId");
        if (invoiceId != null) {
            ctx.order.setInvoiceId(UUID.fromString(String.valueOf(invoiceId)));
        }
        touch(ctx, CheckoutSagaState.PAYMENT_CAPTURED, "capture-on-dispatch", null);
        ctx.order.setStatus(CheckoutSagaState.PAYMENT_CAPTURED.name());
        orders.save(ctx.order);
        return CheckoutSagaState.PAYMENT_CAPTURED;
    }

    private void touch(Ctx ctx, CheckoutSagaState state, String step, String error) {
        if (ctx.saga == null) {
            return;
        }
        ctx.saga.setState(state.name());
        ctx.saga.setLastStep(step);
        ctx.saga.setErrorMessage(error);
        sagas.save(ctx.saga);
    }

    private SagaStep<Ctx> step(
            String name,
            java.util.function.Function<Ctx, CheckoutSagaState> execute,
            java.util.function.Consumer<Ctx> compensate
    ) {
        return new SagaStep<>() {
            @Override
            public String name() {
                return name;
            }

            @Override
            public CheckoutSagaState execute(Ctx context) {
                return execute.apply(context);
            }

            @Override
            public void compensate(Ctx context) {
                compensate.accept(context);
            }
        };
    }
}
