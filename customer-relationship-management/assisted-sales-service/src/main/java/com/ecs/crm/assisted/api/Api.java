package com.ecs.crm.assisted.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.UUID;
@RestController
@RequestMapping("/api/v1/assisted-sales")
public class Api {
    @PostMapping("/paylinks")
    public ApiResponse<Map<String, String>> paylink(@RequestBody Map<String, String> body) {
        String token = UUID.randomUUID().toString();
        return ApiResponse.ok(Map.of(
                "customerMobile", body.get("mobile"),
                "paylink", "https://shop.ecs.local/pay/" + token,
                "channel", "WHATSAPP"
        ));
    }
}
