package com.ecs.mec.product.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;

@Entity
@Table(name = "product")
public class Product extends BaseEntity {

    @Column(nullable = false, unique = true, length = 64)
    private String sku;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(length = 8)
    private String hsnCode;

    @Column(length = 80)
    private String brand;

    @Column(length = 255)
    private String categoryPath;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private ProductLifecycle status = ProductLifecycle.DRAFT;

    @Column(nullable = false)
    private Instant effectiveFrom = Instant.now();

    private Instant effectiveTo;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal listPriceInr = BigDecimal.ZERO;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> attributes;

    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getHsnCode() { return hsnCode; }
    public void setHsnCode(String hsnCode) { this.hsnCode = hsnCode; }
    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }
    public String getCategoryPath() { return categoryPath; }
    public void setCategoryPath(String categoryPath) { this.categoryPath = categoryPath; }
    public ProductLifecycle getStatus() { return status; }
    public void setStatus(ProductLifecycle status) { this.status = status; }
    public Instant getEffectiveFrom() { return effectiveFrom; }
    public void setEffectiveFrom(Instant effectiveFrom) { this.effectiveFrom = effectiveFrom; }
    public Instant getEffectiveTo() { return effectiveTo; }
    public void setEffectiveTo(Instant effectiveTo) { this.effectiveTo = effectiveTo; }
    public BigDecimal getListPriceInr() { return listPriceInr; }
    public void setListPriceInr(BigDecimal listPriceInr) { this.listPriceInr = listPriceInr; }
    public Map<String, Object> getAttributes() { return attributes; }
    public void setAttributes(Map<String, Object> attributes) { this.attributes = attributes; }
}
