package com.eaps.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

/**
 * Maps the JSON response FROM the FastAPI ML service's {@code POST /predict}.
 * <p>
 * Response example:
 * <pre>
 * {
 *   "prediction": "LEAVE",
 *   "probability": 0.7234,
 *   "risk_level": "HIGH",
 *   "model_version": "rf_tuned_v2",
 *   "decision_threshold": 0.4273
 * }
 * </pre>
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MlServiceResponse {

    private String prediction;       // "STAY" / "LEAVE"

    private Double probability;      // 0.0 – 1.0

    @JsonProperty("risk_level")
    private String riskLevel;        // "LOW" / "MEDIUM" / "HIGH"

    @JsonProperty("model_version")
    private String modelVersion;

    @JsonProperty("decision_threshold")
    private Double decisionThreshold;
}
