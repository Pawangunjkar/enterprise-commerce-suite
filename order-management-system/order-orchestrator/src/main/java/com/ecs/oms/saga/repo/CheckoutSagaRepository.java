package com.ecs.oms.saga.repo;

import com.ecs.oms.saga.domain.CheckoutSaga;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface CheckoutSagaRepository extends JpaRepository<CheckoutSaga, UUID> {
    Optional<CheckoutSaga> findByOrderId(UUID orderId);
}
