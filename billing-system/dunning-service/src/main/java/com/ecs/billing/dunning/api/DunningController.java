package com.ecs.billing.dunning.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/dunning")
public class DunningController {
    @GetMapping("/schedule")
    public ApiResponse<List<Map<String, Object>>> schedule() {
        return ApiResponse.ok(List.of(
                Map.of("attempt", 1, "delayHours", 0),
                Map.of("attempt", 2, "delayHours", 24),
                Map.of("attempt", 3, "delayHours", 72)
        ));
    }
}
