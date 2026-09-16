package com.ecs.crm.customer.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
@RestController
@RequestMapping("/api/v1/customers")
public class Api {
    private final Map<String, Map<String, Object>> store = new ConcurrentHashMap<>();
    public record OtpStart(String mobile) {}
    public record OtpVerify(String mobile, String otp) {}
    public record Profile(String mobile, String pan, String gstin, String name) {}

    @PostMapping("/otp/start")
    public ApiResponse<Map<String, String>> start(@RequestBody OtpStart request) {
        if (request.mobile() == null || !request.mobile().matches("^[6-9]\\d{9}$")) {
            throw DomainException.badRequest("Invalid Indian mobile number");
        }
        merge(request.mobile(), Map.of("mobile", request.mobile(), "otp", "123456", "kycStatus", "PENDING"));
        return ApiResponse.ok(Map.of("status", "OTP_SENT"));
    }

    @PostMapping("/otp/verify")
    public ApiResponse<Map<String, Object>> verify(@RequestBody OtpVerify request) {
        if (!"123456".equals(request.otp())) throw DomainException.unprocessable("OTP_INVALID", "Incorrect OTP");
        merge(request.mobile(), Map.of("mobile", request.mobile(), "kycStatus", "VERIFIED"));
        return ApiResponse.ok(Map.of("mobile", request.mobile(), "kycStatus", "VERIFIED"));
    }

    @PutMapping("/{mobile}")
    public ApiResponse<Profile> upsert(@PathVariable String mobile, @RequestBody Profile profile) {
        merge(mobile, Map.of(
                "mobile", mobile,
                "pan", nullToEmpty(profile.pan()),
                "gstin", nullToEmpty(profile.gstin()),
                "name", nullToEmpty(profile.name())
        ));
        return ApiResponse.ok(new Profile(mobile, profile.pan(), profile.gstin(), profile.name()));
    }

    @GetMapping("/{mobile}")
    public ApiResponse<Map<String, Object>> get(@PathVariable String mobile) {
        Map<String, Object> row = store.get(mobile);
        if (row == null) {
            throw DomainException.notFound("customer", mobile);
        }
        Map<String, Object> view = new HashMap<>(row);
        view.remove("otp");
        return ApiResponse.ok(view);
    }

    private void merge(String mobile, Map<String, Object> patch) {
        store.compute(mobile, (key, existing) -> {
            Map<String, Object> next = existing == null ? new HashMap<>() : new HashMap<>(existing);
            next.putAll(patch);
            return next;
        });
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }
}
