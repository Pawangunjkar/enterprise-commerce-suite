package com.ecs.billing.pay.repo;

import com.ecs.billing.pay.domain.PaymentTxn;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface PaymentTxnRepository extends JpaRepository<PaymentTxn, UUID> {
}
