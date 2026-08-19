package com.ecs.dlq.repo;

import com.ecs.dlq.domain.DeadLetter;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface DeadLetterRepository extends JpaRepository<DeadLetter, UUID> {
    Page<DeadLetter> findByStatus(String status, Pageable pageable);
}
