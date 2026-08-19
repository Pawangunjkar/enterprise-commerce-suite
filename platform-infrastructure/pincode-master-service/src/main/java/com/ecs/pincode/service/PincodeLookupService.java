package com.ecs.pincode.service;

import com.ecs.common.core.cache.EcsCacheConfiguration;
import com.ecs.common.core.exception.DomainException;
import com.ecs.pincode.domain.Pincode;
import com.ecs.pincode.repo.PincodeRepository;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Map;

@Service
public class PincodeLookupService {

    private final PincodeRepository repository;

    public PincodeLookupService(PincodeRepository repository) {
        this.repository = repository;
    }

    @Cacheable(cacheNames = EcsCacheConfiguration.PINCODES, key = "#pincode")
    public Pincode require(String pincode) {
        return repository.findByPincode(pincode)
                .orElseThrow(() -> DomainException.notFound("Pincode", pincode));
    }

    @Cacheable(cacheNames = EcsCacheConfiguration.SERVICEABILITY, key = "#origin + ':' + #pincode")
    public Map<String, Object> serviceability(String pincode, String origin) {
        Pincode dest = require(pincode);
        Pincode orig = repository.findByPincode(origin).orElse(dest);
        int days = dest.getStandardTransitDays();
        if (dest.isOda()) {
            days += 2;
        }
        if (!orig.getStateCode().equals(dest.getStateCode())) {
            days += 1;
        }
        return Map.of(
                "pincode", dest.getPincode(),
                "serviceable", dest.isServiceable(),
                "oda", dest.isOda(),
                "city", dest.getCity(),
                "stateCode", dest.getStateCode(),
                "originStateCode", orig.getStateCode(),
                "intraState", orig.getStateCode().equals(dest.getStateCode()),
                "edd", LocalDate.now().plusDays(days).toString(),
                "transitDays", days
        );
    }
}
