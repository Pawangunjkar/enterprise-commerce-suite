package com.ecs.oms.saga.domain;

import com.ecs.common.core.domain.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

import java.math.BigDecimal;

@Entity
@Table(name = "affinity_rule")
public class AffinityRule extends BaseEntity {

    @Column(nullable = false, length = 64)
    private String anchorSku;

    @Column(nullable = false, length = 64)
    private String suggestedSku;

    @Column(nullable = false, length = 16)
    private String suggestionType;

    @Column(nullable = false, precision = 8, scale = 4)
    private BigDecimal score;

    @Column(nullable = false, length = 255)
    private String reason;

    public String getAnchorSku() { return anchorSku; }
    public String getSuggestedSku() { return suggestedSku; }
    public String getSuggestionType() { return suggestionType; }
    public BigDecimal getScore() { return score; }
    public String getReason() { return reason; }
}
