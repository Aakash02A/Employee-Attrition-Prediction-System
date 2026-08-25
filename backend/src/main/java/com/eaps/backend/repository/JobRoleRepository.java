package com.eaps.backend.repository;

import com.eaps.backend.model.JobRole;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface JobRoleRepository extends JpaRepository<JobRole, Long> {

    Optional<JobRole> findByTitle(String title);
}
