package com.ecs.crm.address.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/addresses")
public class Api {
    @GetMapping("/autofill")
    public ApiResponse<Map<String, String>> autofill(@RequestParam String pincode) {
        return ApiResponse.ok(Map.of("pincode", pincode, "city", "New Delhi", "state", "Delhi", "stateCode", "DL"));
    }
}
