package com.ecs.billing.gst;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;

class GstCalculatorTest {

    @Test
    void intraStateSplitsCgstSgst() {
        var result = GstCalculator.compute(new BigDecimal("1000.00"), 18, "DL", "DL");
        assertEquals("CGST_SGST", result.taxType());
        assertEquals(new BigDecimal("90.00"), result.cgst());
        assertEquals(new BigDecimal("90.00"), result.sgst());
        assertEquals(new BigDecimal("0.00"), result.igst());
        assertEquals(new BigDecimal("1180.00"), result.total());
    }

    @Test
    void interStateUsesIgst() {
        var result = GstCalculator.compute(new BigDecimal("1000.00"), 18, "HR", "MH");
        assertEquals("IGST", result.taxType());
        assertEquals(new BigDecimal("180.00"), result.igst());
        assertEquals(new BigDecimal("0.00"), result.cgst());
    }
}
