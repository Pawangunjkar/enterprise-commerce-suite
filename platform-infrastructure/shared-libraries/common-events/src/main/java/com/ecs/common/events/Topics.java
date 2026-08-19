package com.ecs.common.events;

public final class Topics {
    public static final String CATALOG_PRODUCT_PUBLISHED = "catalog.product-published";
    public static final String CATALOG_OFFER_SYNCED = "catalog.offer-synced";
    public static final String CATALOG_OFFER_ACTIVATED = "catalog.offer-activated";
    public static final String CATALOG_PRODUCT_ACTIVATED = "catalog.product-activated";
    public static final String PRICING_EOD_UPDATE = "pricing.eod-update";
    public static final String ORDER_PLACED = "order.placed";
    public static final String ORDER_STATUS_CHANGED = "order.status-changed";
    public static final String PAYMENT_AUTHORIZED = "billing.payment-authorized";
    public static final String PAYMENT_CAPTURED = "billing.payment-captured";
    public static final String PAYMENT_FAILED = "billing.payment-failed";
    public static final String INVOICE_ISSUED = "billing.invoice-issued";
    public static final String SHIPMENT_CREATED = "logistics.shipment-created";
    public static final String NDR_RAISED = "logistics.ndr-raised";
    public static final String CART_ABANDONED = "crm.cart-abandoned";
    public static final String CUSTOMER_KYC_UPDATED = "crm.kyc-updated";
    public static final String DLQ = "platform.dlq";
    public static final String AUDIT = "platform.mca-audit";

    private Topics() {}
}
