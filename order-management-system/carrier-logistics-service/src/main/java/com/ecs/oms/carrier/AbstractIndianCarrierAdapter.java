package com.ecs.oms.carrier;

import com.ecs.logistics.spi.CarrierAdapter;
import com.ecs.logistics.spi.NdrStatus;
import com.ecs.logistics.spi.ServiceabilityRequest;
import com.ecs.logistics.spi.ServiceabilityResponse;
import com.ecs.logistics.spi.WaybillRequest;
import com.ecs.logistics.spi.WaybillResponse;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Base64;
import java.util.UUID;

abstract class AbstractIndianCarrierAdapter implements CarrierAdapter {

    private final String id;
    private final String awbPrefix;
    private final String trackBase;
    private final BigDecimal baseRate;

    protected AbstractIndianCarrierAdapter(String id, String awbPrefix, String trackBase, BigDecimal baseRate) {
        this.id = id;
        this.awbPrefix = awbPrefix;
        this.trackBase = trackBase;
        this.baseRate = baseRate;
    }

    @Override
    public String carrierId() {
        return id;
    }

    @Override
    public ServiceabilityResponse checkServiceability(ServiceabilityRequest request) {
        int days = request.destinationPincode().startsWith("1") ? 2 : 4;
        if (request.cod()) {
            days += 1;
        }
        return new ServiceabilityResponse(true, false, baseRate, days, LocalDate.now().plusDays(days), "N1");
    }

    @Override
    public WaybillResponse createWaybill(WaybillRequest request) {
        String awb = awbPrefix + UUID.randomUUID().toString().substring(0, 10).toUpperCase();
        return new WaybillResponse(id, awb, Base64.getEncoder().encodeToString(("AWB " + awb).getBytes()), trackBase + awb);
    }

    @Override
    public NdrStatus fetchNdr(String awb) {
        return new NdrStatus(awb, "CNA", "Consignee not available", 1, Instant.now(), false);
    }

    @Override
    public byte[] reprintLabel(String awb) {
        return ("LABEL-" + awb).getBytes();
    }
}
