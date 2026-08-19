package com.ecs.billing.webhook.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/payments/webhooks")
public class WebhookController {
    @PostMapping("/{provider}")
    public ApiResponse<Map<String, String>> ingest(@PathVariable String provider, @RequestHeader(value = "X-Signature", required = false) String signature) {
        return ApiResponse.ok(Map.of("provider", provider, "accepted", "true", "signaturePresent", String.valueOf(signature != null)));
    }
}
