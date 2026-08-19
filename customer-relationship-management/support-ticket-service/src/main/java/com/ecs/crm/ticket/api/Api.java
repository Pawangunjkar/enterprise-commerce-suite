package com.ecs.crm.ticket.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
@RestController
@RequestMapping("/api/v1/tickets")
public class Api {
    @PostMapping
    public ApiResponse<Map<String, Object>> create(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of(
                "ticketId", UUID.randomUUID().toString(),
                "priority", body.getOrDefault("priority", "P2"),
                "slaDueAt", Instant.now().plusSeconds(14400).toString(),
                "status", "OPEN"
        ));
    }
}
