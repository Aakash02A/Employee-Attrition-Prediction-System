package com.eaps.backend.dto;

import lombok.*;

import java.time.LocalDateTime;

/**
 * Response body for a prediction result returned to the frontend.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PredictionResponse {

    private Long id;
    private Long employeeId;
    private String empCode;
    private String employeeDepartment;
    private String employeeJobRole;

    private String prediction;        // "STAY" / "LEAVE"
    private Double probability;       // 0.0 – 1.0
    private String riskLevel;         // "LOW" / "MEDIUM" / "HIGH"
    private String modelVersion;
    private Double decisionThreshold;
    private String requestedBy;       // username of the requester
    private LocalDateTime createdAt;
}
