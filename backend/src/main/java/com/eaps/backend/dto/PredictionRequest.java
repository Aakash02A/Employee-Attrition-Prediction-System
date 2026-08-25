package com.eaps.backend.dto;

import jakarta.validation.constraints.NotNull;
import lombok.*;

/**
 * Request body for running an attrition prediction.
 * Only the employee ID is needed — the service fetches the employee's
 * attributes from the database and sends them to the ML service.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PredictionRequest {

    @NotNull(message = "Employee ID is required")
    private Long employeeId;
}
