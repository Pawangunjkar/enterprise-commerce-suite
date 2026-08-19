package com.ecs.mec.variant.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/catalog/variants")
public class VariantMatrixController {

    public record Axis(String name, List<String> values, Map<String, BigDecimal> priceDelta) {}
    public record Request(String baseSku, BigDecimal basePrice, List<Axis> axes) {}
    public record SkuVariant(String sku, Map<String, String> options, BigDecimal price) {}

    @PostMapping("/explode")
    public ApiResponse<List<SkuVariant>> explode(@RequestBody Request request) {
        List<SkuVariant> variants = new ArrayList<>();
        explode(request, 0, new LinkedHashMap<>(), BigDecimal.ZERO, variants);
        return ApiResponse.ok(variants);
    }

    private void explode(Request request, int axisIndex, Map<String, String> current, BigDecimal delta,
                         List<SkuVariant> out) {
        if (axisIndex == request.axes().size()) {
            String suffix = String.join("-", current.values()).replace(" ", "").toUpperCase();
            out.add(new SkuVariant(request.baseSku() + "-" + suffix, Map.copyOf(current), request.basePrice().add(delta)));
            return;
        }
        Axis axis = request.axes().get(axisIndex);
        for (String value : axis.values()) {
            current.put(axis.name(), value);
            BigDecimal add = axis.priceDelta() == null ? BigDecimal.ZERO : axis.priceDelta().getOrDefault(value, BigDecimal.ZERO);
            explode(request, axisIndex + 1, current, delta.add(add), out);
            current.remove(axis.name());
        }
    }
}
