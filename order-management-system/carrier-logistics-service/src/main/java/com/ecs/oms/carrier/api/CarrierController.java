package com.ecs.oms.carrier.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.logistics.spi.CarrierAdapter;
import com.ecs.logistics.spi.ServiceabilityRequest;
import com.ecs.logistics.spi.WaybillRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/logistics")
public class CarrierController {
    private final Map<String, CarrierAdapter> adapters;

    public CarrierController(List<CarrierAdapter> adapters) {
        this.adapters = adapters.stream().collect(Collectors.toMap(a -> a.carrierId().toLowerCase(), Function.identity()));
    }

    @PostMapping("/{carrier}/serviceability")
    public ApiResponse<?> serviceability(@PathVariable String carrier, @RequestBody ServiceabilityRequest request) {
        return ApiResponse.ok(adapter(carrier).checkServiceability(request));
    }

    @PostMapping("/{carrier}/waybills")
    public ApiResponse<?> waybill(@PathVariable String carrier, @RequestBody WaybillRequest request) {
        return ApiResponse.ok(adapter(carrier).createWaybill(request));
    }

    private CarrierAdapter adapter(String carrier) {
        CarrierAdapter adapter = adapters.get(carrier.toLowerCase());
        if (adapter == null) {
            throw com.ecs.common.core.exception.DomainException.notFound("Carrier", carrier);
        }
        return adapter;
    }
}
