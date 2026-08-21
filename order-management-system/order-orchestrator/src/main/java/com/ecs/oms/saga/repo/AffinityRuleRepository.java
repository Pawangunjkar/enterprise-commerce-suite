package com.ecs.oms.saga.repo;

import com.ecs.oms.saga.domain.AffinityRule;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.UUID;

public interface AffinityRuleRepository extends JpaRepository<AffinityRule, UUID> {
    List<AffinityRule> findByAnchorSkuIn(Collection<String> anchorSkus);
}
