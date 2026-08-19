package com.ecs.mec.temporal.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/catalog/time-travel")
public class TimeTravelController {

    @GetMapping
    public ApiResponse<Map<String, String>> preview(@RequestParam Instant asOf) {
        return ApiResponse.ok(Map.of(
                "asOf", asOf.toString(),
                "solrFq", "effective_from_dt:[* TO " + asOf + "] AND effective_to_dt:[" + asOf + " TO *]"
        ));
    }
}
