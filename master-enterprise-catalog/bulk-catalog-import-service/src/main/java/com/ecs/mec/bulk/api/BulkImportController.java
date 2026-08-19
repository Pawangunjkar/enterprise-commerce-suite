package com.ecs.mec.bulk.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/api/v1/catalog/imports")
public class BulkImportController {

    @PostMapping
    public ApiResponse<Map<String, Integer>> importCsv(@RequestParam("file") MultipartFile file) throws Exception {
        AtomicInteger lines = new AtomicInteger();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {
            reader.lines().skip(1).forEach(l -> lines.incrementAndGet());
        }
        return ApiResponse.ok(Map.of("acceptedRows", lines.get()));
    }
}
