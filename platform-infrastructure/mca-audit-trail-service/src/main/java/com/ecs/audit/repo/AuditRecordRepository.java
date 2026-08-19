package com.ecs.audit.repo;

import com.ecs.audit.domain.AuditRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface AuditRecordRepository extends JpaRepository<AuditRecord, UUID> {
    Page<AuditRecord> findByTenantIdAndResourceType(String tenantId, String resourceType, Pageable pageable);
}
