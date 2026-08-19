package com.ecs.mec.dam.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/catalog/media")
public class DamController {

    @PostMapping
    public ApiResponse<Map<String, String>> upload(@RequestParam("file") MultipartFile file) {
        String assetId = UUID.randomUUID().toString();
        return ApiResponse.ok(Map.of(
                "assetId", assetId,
                "originalName", file.getOriginalFilename() == null ? "unknown" : file.getOriginalFilename(),
                "contentType", file.getContentType() == null ? "application/octet-stream" : file.getContentType(),
                "webpUrl", "http://localhost:9000/ecs-dam/" + assetId + ".webp"
        ));
    }
}
