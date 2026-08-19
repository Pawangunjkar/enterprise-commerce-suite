package com.ecs.crm.abandon.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.events.Topics;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/carts/abandonment")
public class Api {
    private final KafkaTemplate<String, String> kafka;
    public Api(KafkaTemplate<String, String> kafka) { this.kafka = kafka; }
    @PostMapping
    public ApiResponse<Map<String, String>> mark(@RequestBody Map<String, String> body) {
        kafka.send(Topics.CART_ABANDONED, body.get("cartId"), body.toString());
        return ApiResponse.ok(Map.of("status", "RECOVERY_QUEUED", "channel", "WHATSAPP"));
    }
}
