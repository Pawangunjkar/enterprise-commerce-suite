package com.ecs.oms.carrier;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class ShiprocketAdapter extends AbstractIndianCarrierAdapter {
    public ShiprocketAdapter() {
        super("SHIPROCKET", "SRK", "https://shiprocket.co/tracking/", BigDecimal.valueOf(69));
    }
}
