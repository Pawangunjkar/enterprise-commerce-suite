package com.ecs.billing.gst.api;

import com.ecs.billing.gst.GstCalculator;
import com.ecs.billing.gst.GstTaxService;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/gst")
public class GstController {
    private final GstTaxService gstTaxService;

    public GstController(GstTaxService gstTaxService) {
        this.gstTaxService = gstTaxService;
    }

    public record ComputeRequest(BigDecimal taxable, int slab, String originState, String destState, String hsn) {}

    @PostMapping("/compute")
    public ApiResponse<GstCalculator.GstBreakdown> compute(@RequestBody ComputeRequest request) {
        return ApiResponse.ok(gstTaxService.compute(request.taxable(), request.slab(), request.originState(), request.destState()));
    }

    @PostMapping("/eway-bill")
    public ApiResponse<Map<String, Object>> eway(@RequestBody ComputeRequest request) {
        boolean required = request.taxable().compareTo(BigDecimal.valueOf(50000)) > 0;
        return ApiResponse.ok(Map.of(
                "required", required,
                "hsn", request.hsn(),
                "taxableValue", request.taxable(),
                "originState", request.originState(),
                "destState", request.destState()
        ));
    }
}
