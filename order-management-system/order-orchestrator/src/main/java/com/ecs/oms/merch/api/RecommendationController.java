package com.ecs.oms.merch.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.oms.merch.RecommendationEngine;
import com.ecs.oms.merch.RecommendationService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/recommendations")
public class RecommendationController {

    private final RecommendationService service;

    public RecommendationController(RecommendationService service) {
        this.service = service;
    }

    public record SuggestRequest(List<String> skus, String customerId, Integer limit) {}

    @PostMapping
    public ApiResponse<RecommendationEngine.Bundle> suggest(@RequestBody SuggestRequest request) {
        int limit = request.limit() == null ? 5 : request.limit();
        return ApiResponse.ok(service.suggest(request.skus(), limit));
    }
}
