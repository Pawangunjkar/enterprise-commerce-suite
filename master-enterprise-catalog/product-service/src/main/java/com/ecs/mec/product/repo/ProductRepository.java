package com.ecs.mec.product.repo;

import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.domain.ProductLifecycle;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ProductRepository extends JpaRepository<Product, UUID> {
    Optional<Product> findBySku(String sku);
    List<Product> findByStatusAndEffectiveFromLessThanEqual(ProductLifecycle status, Instant when);
}
