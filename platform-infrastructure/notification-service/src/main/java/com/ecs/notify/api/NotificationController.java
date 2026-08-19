package com.ecs.notify.api;

import com.ecs.common.core.api.ApiResponse;
import jakarta.validation.constraints.NotBlank;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/notifications")
public class NotificationController {
    private static final Logger log = LoggerFactory.getLogger(NotificationController.class);

    public record NotifyRequest(
            @NotBlank String channel,
            @NotBlank String to,
            @NotBlank String template,
            Map<String, String> params
    ) {}

    @PostMapping
    public ApiResponse<Map<String, String>> send(@RequestBody NotifyRequest request) {
        String messageId = UUID.randomUUID().toString();
        log.info("Dispatching {} to {} template={} id={}", request.channel(), request.to(), request.template(), messageId);
        return ApiResponse.ok(Map.of(
                "messageId", messageId,
                "channel", request.channel(),
                "status", "QUEUED"
        ));
    }
}
