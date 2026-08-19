package com.ecs.billing.gst;

import com.ecs.common.core.cache.EcsCacheConfiguration;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

@Service
public class GstTaxService {

    @Cacheable(cacheNames = EcsCacheConfiguration.GST,
            key = "#taxable.toPlainString() + ':' + #slab + ':' + #originState + ':' + #destState")
    public GstCalculator.GstBreakdown compute(BigDecimal taxable, int slab, String originState, String destState) {
        return GstCalculator.compute(taxable, slab, originState, destState);
    }
}
