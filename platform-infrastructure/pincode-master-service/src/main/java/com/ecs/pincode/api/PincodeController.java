package com.ecs.pincode.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.pincode.domain.Pincode;
import com.ecs.pincode.service.PincodeLookupService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/pincodes")
public class PincodeController {

    private final PincodeLookupService lookupService;

    public PincodeController(PincodeLookupService lookupService) {
        this.lookupService = lookupService;
    }

    @GetMapping("/{pincode}")
    public ApiResponse<Pincode> get(@PathVariable String pincode) {
        return ApiResponse.ok(lookupService.require(pincode));
    }

    @GetMapping("/{pincode}/serviceability")
    public ApiResponse<Map<String, Object>> serviceability(
            @PathVariable String pincode,
            @RequestParam(defaultValue = "110001") String origin
    ) {
        return ApiResponse.ok(lookupService.serviceability(pincode, origin));
    }
}
