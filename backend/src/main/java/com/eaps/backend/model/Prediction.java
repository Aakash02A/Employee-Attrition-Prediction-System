package com.eaps.backend.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * JPA entity for the {@code predictions} table.
 * Stores every attrition prediction result, linked to the employee and
 * the user who requested it.
 */
@Entity
@Table(name = "predictions")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "employee_id", nullable = false)
    private Employee employee;

    @Column(nullable = false, length = 10)
    private String prediction; // "STAY" / "LEAVE"

    @Column(nullable = false)
    private Double probability; // 0.0 – 1.0

    @Column(name = "risk_level", nullable = false, length = 10)
    private String riskLevel; // "LOW" / "MEDIUM" / "HIGH"

    @Column(name = "model_version", nullable = false, length = 50)
    private String modelVersion;

    @Column(name = "decision_threshold", nullable = false)
    private Double decisionThreshold;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "requested_by", nullable = false)
    private AppUser requestedBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
