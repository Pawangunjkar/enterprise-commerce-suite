package com.ecs.mec.imei.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/api/v1/imei")
public class ImeiController {
    private static final Pattern IMEI = Pattern.compile("\\d{15}");

    public record IngestRequest(String sku, String imei1, String imei2, String serial) {}
    public record IngestResult(String sku, String imei1, String imei2, String serial, boolean valid) {}

    @PostMapping("/ingest")
    public ApiResponse<IngestResult> ingest(@RequestBody IngestRequest request) {
        List<String> errors = new ArrayList<>();
        if (!luhn(request.imei1())) errors.add("IMEI1 failed Luhn check");
        if (request.imei2() != null && !request.imei2().isBlank() && !luhn(request.imei2())) errors.add("IMEI2 failed Luhn check");
        if (!errors.isEmpty()) {
            throw DomainException.badRequest(String.join("; ", errors));
        }
        return ApiResponse.ok(new IngestResult(request.sku(), request.imei1(), request.imei2(), request.serial(), true));
    }

    static boolean luhn(String value) {
        if (value == null || !IMEI.matcher(value).matches()) return false;
        int sum = 0;
        boolean alt = false;
        for (int i = value.length() - 1; i >= 0; i--) {
            int n = value.charAt(i) - '0';
            if (alt) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            sum += n;
            alt = !alt;
        }
        return sum % 10 == 0;
    }
}
