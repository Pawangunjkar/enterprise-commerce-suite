package com.ecs.oms.saga.repo;

import com.ecs.oms.saga.domain.CommerceOrder;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface CommerceOrderRepository extends JpaRepository<CommerceOrder, UUID> {
    Optional<CommerceOrder> findByOrderNumber(String orderNumber);
}
