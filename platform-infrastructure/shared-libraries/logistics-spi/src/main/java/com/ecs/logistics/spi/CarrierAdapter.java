package com.ecs.logistics.spi;

public interface CarrierAdapter {
    String carrierId();

    ServiceabilityResponse checkServiceability(ServiceabilityRequest request);

    WaybillResponse createWaybill(WaybillRequest request);

    NdrStatus fetchNdr(String awb);

    byte[] reprintLabel(String awb);
}
