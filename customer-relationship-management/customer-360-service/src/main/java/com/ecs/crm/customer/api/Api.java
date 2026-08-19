package com.ecs.crm.customer.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;
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
        store.put(request.mobile(), Map.of("otp", "123456"));
        return ApiResponse.ok(Map.of("status", "OTP_SENT"));
    }

    @PostMapping("/otp/verify")
    public ApiResponse<Map<String, Object>> verify(@RequestBody OtpVerify request) {
        if (!"123456".equals(request.otp())) throw DomainException.unprocessable("OTP_INVALID", "Incorrect OTP");
        return ApiResponse.ok(Map.of("mobile", request.mobile(), "kycStatus", "PENDING"));
    }

    @PutMapping("/{mobile}")
    public ApiResponse<Profile> upsert(@PathVariable String mobile, @RequestBody Profile profile) {
        return ApiResponse.ok(new Profile(mobile, profile.pan(), profile.gstin(), profile.name()));
    }
}
