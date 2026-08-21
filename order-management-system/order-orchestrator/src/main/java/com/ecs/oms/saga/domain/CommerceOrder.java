package com.ecs.oms.saga.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "commerce_order")
public class CommerceOrder extends BaseEntity {

    @Column(nullable = false, unique = true, length = 32)
    private String orderNumber;

    @Column(nullable = false, length = 64)
    private String cartId;

    @Column(length = 64)
    private String customerId;

    @Column(nullable = false, length = 6)
    private String pincode;

    @Column(nullable = false, length = 16)
    private String paymentMode;

    @Column(nullable = false, length = 32)
    private String status;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal grandTotalInr;

    @Column(nullable = false, length = 2)
    private String originState = "HR";

    @Column(nullable = false, length = 2)
    private String destState = "DL";

    private UUID paymentId;
    private UUID invoiceId;

    @Column(length = 64)
    private String waveId;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true, fetch = jakarta.persistence.FetchType.EAGER)
    private List<OrderLine> lines = new ArrayList<>();

    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }
    public String getCartId() { return cartId; }
    public void setCartId(String cartId) { this.cartId = cartId; }
    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }
    public String getPincode() { return pincode; }
    public void setPincode(String pincode) { this.pincode = pincode; }
    public String getPaymentMode() { return paymentMode; }
    public void setPaymentMode(String paymentMode) { this.paymentMode = paymentMode; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public BigDecimal getGrandTotalInr() { return grandTotalInr; }
    public void setGrandTotalInr(BigDecimal grandTotalInr) { this.grandTotalInr = grandTotalInr; }
    public String getOriginState() { return originState; }
    public void setOriginState(String originState) { this.originState = originState; }
    public String getDestState() { return destState; }
    public void setDestState(String destState) { this.destState = destState; }
    public UUID getPaymentId() { return paymentId; }
    public void setPaymentId(UUID paymentId) { this.paymentId = paymentId; }
    public UUID getInvoiceId() { return invoiceId; }
    public void setInvoiceId(UUID invoiceId) { this.invoiceId = invoiceId; }
    public String getWaveId() { return waveId; }
    public void setWaveId(String waveId) { this.waveId = waveId; }
    public List<OrderLine> getLines() { return lines; }
    public void addLine(OrderLine line) {
        line.setOrder(this);
        lines.add(line);
    }
}
