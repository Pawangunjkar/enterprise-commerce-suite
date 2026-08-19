package com.ecs.mec.product.service;

import com.ecs.common.core.cache.EcsCacheConfiguration;
import com.ecs.common.core.exception.DomainException;
import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.repo.ProductRepository;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class ProductQueryService {

    private final ProductRepository repository;

    public ProductQueryService(ProductRepository repository) {
        this.repository = repository;
    }

    @Cacheable(cacheNames = EcsCacheConfiguration.PRODUCTS, key = "#id")
    public Product require(UUID id) {
        return repository.findById(id).orElseThrow(() -> DomainException.notFound("Product", id));
    }

    @CacheEvict(cacheNames = EcsCacheConfiguration.PRODUCTS, key = "#id")
    public void evict(UUID id) {
        // cache eviction only
    }
}
