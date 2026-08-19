package com.ecs.pincode.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.pincode.domain.Pincode;
import com.ecs.pincode.repo.PincodeRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/pincodes")
public class PincodeController {

    private final PincodeRepository repository;

    public PincodeController(PincodeRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/{pincode}")
    public ApiResponse<Pincode> get(@PathVariable String pincode) {
        return ApiResponse.ok(repository.findByPincode(pincode)
                .orElseThrow(() -> DomainException.notFound("Pincode", pincode)));
    }

    @GetMapping("/{pincode}/serviceability")
    public ApiResponse<Map<String, Object>> serviceability(
            @PathVariable String pincode,
            @RequestParam(defaultValue = "110001") String origin
    ) {
        Pincode dest = repository.findByPincode(pincode)
                .orElseThrow(() -> DomainException.notFound("Pincode", pincode));
        Pincode orig = repository.findByPincode(origin).orElse(dest);
        int days = dest.getStandardTransitDays();
        if (dest.isOda()) {
            days += 2;
        }
        if (!orig.getStateCode().equals(dest.getStateCode())) {
            days += 1;
        }
        LocalDate edd = LocalDate.now().plusDays(days);
        return ApiResponse.ok(Map.of(
                "pincode", dest.getPincode(),
                "serviceable", dest.isServiceable(),
                "oda", dest.isOda(),
                "city", dest.getCity(),
                "stateCode", dest.getStateCode(),
                "originStateCode", orig.getStateCode(),
                "intraState", orig.getStateCode().equals(dest.getStateCode()),
                "edd", edd.toString(),
                "transitDays", days
        ));
    }
}
