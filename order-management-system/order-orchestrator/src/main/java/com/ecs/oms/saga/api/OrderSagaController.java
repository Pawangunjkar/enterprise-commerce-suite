package com.ecs.oms.saga.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.oms.saga.domain.CommerceOrder;
import com.ecs.oms.saga.service.CheckoutSagaService;
import com.ecs.saga.CheckoutSagaState;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderSagaController {

    private final CheckoutSagaService checkoutSagaService;

    public OrderSagaController(CheckoutSagaService checkoutSagaService) {
        this.checkoutSagaService = checkoutSagaService;
    }

    public record LineRequest(String sku, int qty, BigDecimal unitPriceInr, String hsnCode) {}

    public record PlaceOrderRequest(
            String cartId,
            String pincode,
            String paymentMode,
            BigDecimal amount,
            String customerId,
            String originState,
            String destState,
            List<LineRequest> lines
    ) {}

    public record PlaceOrderResponse(
            UUID orderId,
            String orderNumber,
            CheckoutSagaState state,
            String status,
            UUID paymentId,
            UUID invoiceId,
            String waveId
    ) {}

    @PostMapping
    public ApiResponse<PlaceOrderResponse> place(@RequestBody PlaceOrderRequest request) {
        CheckoutSagaService.PlaceOrderResult result = checkoutSagaService.place(request);
        CommerceOrder order = result.order();
        return ApiResponse.ok(new PlaceOrderResponse(
                order.getId(),
                order.getOrderNumber(),
                result.state(),
                order.getStatus(),
                order.getPaymentId(),
                order.getInvoiceId(),
                order.getWaveId()
        ));
    }

    @GetMapping("/{id}")
    public ApiResponse<CommerceOrder> get(@PathVariable UUID id) {
        return ApiResponse.ok(checkoutSagaService.get(id));
    }
}
