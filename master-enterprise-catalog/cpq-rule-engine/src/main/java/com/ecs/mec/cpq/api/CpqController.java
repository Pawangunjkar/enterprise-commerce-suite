package com.ecs.mec.cpq.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/api/v1/catalog/cpq")
public class CpqController {

    public record CompatibilityRule(String parentSku, Set<String> allowedChildSkus) {}
    public record EvaluateRequest(String parentSku, List<String> selected, List<CompatibilityRule> rules) {}

    @PostMapping("/evaluate")
    public ApiResponse<Boolean> evaluate(@RequestBody EvaluateRequest request) {
        CompatibilityRule rule = request.rules().stream()
                .filter(r -> r.parentSku().equals(request.parentSku()))
                .findFirst()
                .orElseThrow(() -> DomainException.badRequest("No CPQ rule for " + request.parentSku()));
        boolean ok = rule.allowedChildSkus().containsAll(request.selected());
        if (!ok) {
            throw DomainException.unprocessable("INCOMPATIBLE_BOM", "Selected components are not compatible");
        }
        return ApiResponse.ok(true);
    }
}
