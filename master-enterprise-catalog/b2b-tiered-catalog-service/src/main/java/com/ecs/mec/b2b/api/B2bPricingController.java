package com.ecs.mec.b2b.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Comparator;
import java.util.List;

@RestController
@RequestMapping("/api/v1/catalog/b2b")
public class B2bPricingController {

    public record Tier(int minQty, BigDecimal unitPrice) {}
    public record QuoteRequest(String sku, int qty, int moq, List<Tier> tiers) {}
    public record QuoteResponse(String sku, int qty, BigDecimal unitPrice, BigDecimal lineTotal) {}

    @PostMapping("/quote")
    public ApiResponse<QuoteResponse> quote(@RequestBody QuoteRequest request) {
        if (request.qty() < request.moq()) {
            throw DomainException.unprocessable("MOQ_VIOLATION", "Quantity " + request.qty() + " is below MOQ " + request.moq());
        }
        BigDecimal unit = request.tiers().stream()
                .filter(t -> request.qty() >= t.minQty())
                .max(Comparator.comparingInt(Tier::minQty))
                .map(Tier::unitPrice)
                .orElseThrow(() -> DomainException.badRequest("No matching price tier"));
        return ApiResponse.ok(new QuoteResponse(request.sku(), request.qty(), unit,
                unit.multiply(BigDecimal.valueOf(request.qty())).setScale(2, RoundingMode.HALF_UP)));
    }
}
