package com.eaps.backend.model;

import jakarta.persistence.*;
import lombok.*;

/**
 * JPA entity for the {@code job_role} lookup table.
 * Values must match the 9 job roles the ML model was trained on.
 */
@Entity
@Table(name = "job_role")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class JobRole {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String title;
}
