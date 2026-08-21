package com.ecs.billing.invoice.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "gst_invoice")
public class GstInvoice extends BaseEntity {

    @Column(nullable = false, unique = true, length = 40)
    private String invoiceNumber;

    @Column(nullable = false)
    private UUID orderId;

    @Column(nullable = false, length = 32)
    private String orderNumber;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal taxableInr;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal cgstInr;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal sgstInr;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal igstInr;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal totalInr;

    @Column(nullable = false, length = 16)
    private String taxType;

    @Column(nullable = false)
    private int slab;

    @Column(nullable = false, length = 2)
    private String originState;

    @Column(nullable = false, length = 2)
    private String destState;

    @Column(length = 8)
    private String hsnCode;

    public String getInvoiceNumber() { return invoiceNumber; }
    public void setInvoiceNumber(String invoiceNumber) { this.invoiceNumber = invoiceNumber; }
    public UUID getOrderId() { return orderId; }
    public void setOrderId(UUID orderId) { this.orderId = orderId; }
    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }
    public BigDecimal getTaxableInr() { return taxableInr; }
    public void setTaxableInr(BigDecimal taxableInr) { this.taxableInr = taxableInr; }
    public BigDecimal getCgstInr() { return cgstInr; }
    public void setCgstInr(BigDecimal cgstInr) { this.cgstInr = cgstInr; }
    public BigDecimal getSgstInr() { return sgstInr; }
    public void setSgstInr(BigDecimal sgstInr) { this.sgstInr = sgstInr; }
    public BigDecimal getIgstInr() { return igstInr; }
    public void setIgstInr(BigDecimal igstInr) { this.igstInr = igstInr; }
    public BigDecimal getTotalInr() { return totalInr; }
    public void setTotalInr(BigDecimal totalInr) { this.totalInr = totalInr; }
    public String getTaxType() { return taxType; }
    public void setTaxType(String taxType) { this.taxType = taxType; }
    public int getSlab() { return slab; }
    public void setSlab(int slab) { this.slab = slab; }
    public String getOriginState() { return originState; }
    public void setOriginState(String originState) { this.originState = originState; }
    public String getDestState() { return destState; }
    public void setDestState(String destState) { this.destState = destState; }
    public String getHsnCode() { return hsnCode; }
    public void setHsnCode(String hsnCode) { this.hsnCode = hsnCode; }
}
