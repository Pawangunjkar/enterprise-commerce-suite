package com.ecs.common.core.cache;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import java.time.Duration;

@Configuration
@EnableCaching
@ConditionalOnClass(Caffeine.class)
public class EcsCacheConfiguration {

    public static final String PINCODES = "pincodes";
    public static final String SERVICEABILITY = "serviceability";
    public static final String PRODUCTS = "products";
    public static final String GST = "gst";
    public static final String PRICES = "prices";

    @Bean
    @Primary
    public CacheManager caffeineCacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager(
                PINCODES, SERVICEABILITY, PRODUCTS, GST, PRICES);
        manager.setCaffeine(Caffeine.newBuilder()
                .maximumSize(20_000)
                .expireAfterWrite(Duration.ofMinutes(10))
                .recordStats());
        return manager;
    }
}
