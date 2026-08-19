package com.ecs.billing.gst;

import com.ecs.common.core.exception.DomainException;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Set;

public final class GstCalculator {
    private static final Set<Integer> SLABS = Set.of(0, 5, 12, 18, 28);

    public record GstBreakdown(BigDecimal taxable, BigDecimal cgst, BigDecimal sgst, BigDecimal igst, BigDecimal total,
                               String taxType, int slab) {}

    public static GstBreakdown compute(BigDecimal taxable, int slab, String originState, String destState) {
        if (!SLABS.contains(slab)) {
            throw DomainException.badRequest("Invalid GST slab: " + slab);
        }
        BigDecimal rate = BigDecimal.valueOf(slab).divide(BigDecimal.valueOf(100), 6, RoundingMode.HALF_UP);
        boolean intra = originState.equalsIgnoreCase(destState);
        if (intra) {
            BigDecimal half = taxable.multiply(rate).divide(BigDecimal.valueOf(2), 2, RoundingMode.HALF_UP);
            BigDecimal total = taxable.add(half).add(half);
            return new GstBreakdown(taxable, half, half, BigDecimal.ZERO.setScale(2), total, "CGST_SGST", slab);
        }
        BigDecimal igst = taxable.multiply(rate).setScale(2, RoundingMode.HALF_UP);
        return new GstBreakdown(taxable, BigDecimal.ZERO.setScale(2), BigDecimal.ZERO.setScale(2), igst,
                taxable.add(igst), "IGST", slab);
    }
}
