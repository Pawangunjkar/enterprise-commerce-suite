package com.ecs.billing.invoice.repo;

import com.ecs.billing.invoice.domain.GstInvoice;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface GstInvoiceRepository extends JpaRepository<GstInvoice, UUID> {
}
