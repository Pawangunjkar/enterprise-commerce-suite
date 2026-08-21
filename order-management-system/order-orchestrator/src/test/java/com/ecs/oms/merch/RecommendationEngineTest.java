package com.ecs.oms.merch;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class RecommendationEngineTest {

    private final RecommendationEngine engine = new RecommendationEngine();

    @Test
    void affinitySplitsCrossSellAndUpSellAndHidesCartSkus() {
        var rules = List.of(
                new RecommendationEngine.Affinity("SKU-PHONE-8-128-BLACK", "SKU-BUDS-PRO", "CROSS_SELL", 0.82, "buds"),
                new RecommendationEngine.Affinity("SKU-PHONE-8-128-BLACK", "SKU-PHONE-12-256-GOLD", "UP_SELL", 0.91, "flagship"),
                new RecommendationEngine.Affinity("SKU-PHONE-8-128-BLACK", "SKU-PHONE-8-128-BLACK", "CROSS_SELL", 0.99, "self")
        );
        var result = engine.suggest(List.of("SKU-PHONE-8-128-BLACK"), rules, 5);
        assertEquals(1, result.crossSell().size());
        assertEquals("SKU-BUDS-PRO", result.crossSell().getFirst().sku());
        assertEquals("SKU-PHONE-12-256-GOLD", result.upSell().getFirst().sku());
        assertTrue(result.crossSell().stream().noneMatch(s -> s.sku().contains("PHONE-8")));
    }

    @Test
    void ladderSuggestsNextPhoneWhenAffinityIsMissing() {
        var result = engine.suggest(List.of("SKU-PHONE-8-128-BLACK"), List.of(), 3);
        assertEquals("SKU-PHONE-12-256-GOLD", result.upSell().getFirst().sku());
        assertEquals("LADDER", result.upSell().getFirst().source());
    }

    @Test
    void alreadyOwnedFlagshipIsNotUpsold() {
        var result = engine.suggest(
                List.of("SKU-PHONE-8-128-BLACK", "SKU-PHONE-12-256-GOLD"),
                List.of(),
                3
        );
        assertTrue(result.upSell().isEmpty());
    }
}
