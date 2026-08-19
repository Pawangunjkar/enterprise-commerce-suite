package com.ecs.crm.hierarchy.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/accounts")
public class Api {
    @GetMapping("/tree")
    public ApiResponse<Map<String, Object>> tree() {
        return ApiResponse.ok(Map.of(
                "name", "Acme India Pvt Ltd",
                "gstin", "07AABCU9603R1ZM",
                "children", List.of(
                        Map.of("name", "North Region", "children", List.of(Map.of("name", "Delhi Branch"))),
                        Map.of("name", "West Region", "children", List.of(Map.of("name", "Mumbai Branch")))
                )
        ));
    }
}
