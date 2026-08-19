package com.ecs.pincode.repo;

import com.ecs.pincode.domain.Pincode;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface PincodeRepository extends JpaRepository<Pincode, UUID> {
    Optional<Pincode> findByPincode(String pincode);
}
