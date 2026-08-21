package com.ecs.oms.merch;

import com.ecs.oms.saga.domain.AffinityRule;
import com.ecs.oms.saga.repo.AffinityRuleRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RecommendationService {

    private final AffinityRuleRepository rules;
    private final RecommendationEngine engine = new RecommendationEngine();

    public RecommendationService(AffinityRuleRepository rules) {
        this.rules = rules;
    }

    public RecommendationEngine.Bundle suggest(List<String> skus, int limit) {
        List<String> cart = skus == null ? List.of() : skus.stream().filter(s -> s != null && !s.isBlank()).toList();
        List<RecommendationEngine.Affinity> affinities = cart.isEmpty()
                ? List.of()
                : rules.findByAnchorSkuIn(cart).stream().map(this::toAffinity).toList();
        return engine.suggest(cart, affinities, limit);
    }

    private RecommendationEngine.Affinity toAffinity(AffinityRule rule) {
        return new RecommendationEngine.Affinity(
                rule.getAnchorSku(),
                rule.getSuggestedSku(),
                rule.getSuggestionType(),
                rule.getScore().doubleValue(),
                rule.getReason()
        );
    }
}
