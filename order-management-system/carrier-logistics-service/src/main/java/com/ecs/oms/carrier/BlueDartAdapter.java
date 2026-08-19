package com.ecs.oms.carrier;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class BlueDartAdapter extends AbstractIndianCarrierAdapter {
    public BlueDartAdapter() {
        super("BLUEDART", "BD", "https://www.bluedart.com/tracking/", BigDecimal.valueOf(99));
    }
}
