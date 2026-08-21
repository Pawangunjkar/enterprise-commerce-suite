package com.ecs.oms.merch;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Hybrid merchandising ranker:
 * 1. Affinity / frequently-bought-together rules (cross-sell and up-sell).
 * 2. Same-family SKU ladder (higher RAM/storage) as a deterministic up-sell.
 * Cart SKUs are never recommended back.
 */
public final class RecommendationEngine {

    public record Affinity(String anchorSku, String suggestedSku, String type, double score, String reason) {}

    public record Suggestion(String sku, String type, double score, String reason, String source) {}

    public record Bundle(List<Suggestion> crossSell, List<Suggestion> upSell) {}

    static final List<String> PHONE_LADDER = List.of(
            "SKU-PHONE-8-128-BLACK",
            "SKU-PHONE-12-256-GOLD"
    );

    public Bundle suggest(Collection<String> cartSkus, List<Affinity> rules, int limit) {
        int cap = Math.max(1, Math.min(limit, 12));
        Set<String> cart = new LinkedHashSet<>();
        for (String sku : cartSkus) {
            if (sku != null && !sku.isBlank()) {
                cart.add(sku.trim().toUpperCase(Locale.ROOT));
            }
        }
        Map<String, Suggestion> cross = new HashMap<>();
        Map<String, Suggestion> up = new HashMap<>();
        for (String sku : cart) {
            for (Affinity rule : rules) {
                if (!sku.equalsIgnoreCase(rule.anchorSku())) {
                    continue;
                }
                if (inCart(cart, rule.suggestedSku())) {
                    continue;
                }
                Suggestion suggestion = new Suggestion(
                        rule.suggestedSku(),
                        normalizeType(rule.type()),
                        clamp(rule.score()),
                        rule.reason(),
                        "AFFINITY"
                );
                merge(isUpSell(suggestion.type()) ? up : cross, suggestion);
            }
            ladderUpsell(sku, cart, up);
        }
        return new Bundle(top(cross.values(), cap), top(up.values(), cap));
    }

    private void ladderUpsell(String sku, Set<String> cart, Map<String, Suggestion> up) {
        int idx = indexIgnoreCase(PHONE_LADDER, sku);
        if (idx < 0 || idx >= PHONE_LADDER.size() - 1) {
            return;
        }
        String next = PHONE_LADDER.get(idx + 1);
        if (inCart(cart, next)) {
            return;
        }
        merge(up, new Suggestion(
                next,
                "UP_SELL",
                0.70 + (0.05 * (idx + 1)),
                "Next step-up in the same phone family (RAM/storage)",
                "LADDER"
        ));
    }

    private static void merge(Map<String, Suggestion> into, Suggestion suggestion) {
        String key = suggestion.sku().toUpperCase(Locale.ROOT);
        Suggestion existing = into.get(key);
        if (existing == null || suggestion.score() > existing.score()) {
            into.put(key, suggestion);
        }
    }

    private static List<Suggestion> top(Collection<Suggestion> values, int limit) {
        List<Suggestion> ranked = new ArrayList<>(values);
        ranked.sort(Comparator.comparingDouble(Suggestion::score).reversed()
                .thenComparing(Suggestion::sku));
        return ranked.size() > limit ? List.copyOf(ranked.subList(0, limit)) : List.copyOf(ranked);
    }

    private static boolean inCart(Set<String> cart, String sku) {
        return cart.contains(sku.toUpperCase(Locale.ROOT));
    }

    private static boolean isUpSell(String type) {
        return "UP_SELL".equals(type);
    }

    private static String normalizeType(String type) {
        return type != null && type.equalsIgnoreCase("UP_SELL") ? "UP_SELL" : "CROSS_SELL";
    }

    private static double clamp(double score) {
        return Math.max(0, Math.min(score, 1));
    }

    private static int indexIgnoreCase(List<String> ladder, String sku) {
        for (int i = 0; i < ladder.size(); i++) {
            if (ladder.get(i).equalsIgnoreCase(sku)) {
                return i;
            }
        }
        return -1;
    }
}
