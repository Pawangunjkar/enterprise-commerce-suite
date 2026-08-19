package com.ecs.oms.carrier;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class DelhiveryAdapter extends AbstractIndianCarrierAdapter {
    public DelhiveryAdapter() {
        super("DELHIVERY", "DLV", "https://www.delhivery.com/track/", BigDecimal.valueOf(79));
    }
}
