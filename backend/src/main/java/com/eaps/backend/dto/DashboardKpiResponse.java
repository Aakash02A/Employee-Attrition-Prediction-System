package com.eaps.backend.dto;

import lombok.*;

/**
 * Dashboard KPI response for the frontend's KPI cards.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DashboardKpiResponse {

    private long totalEmployees;
    private long attritionCount;        // predictions with "LEAVE"
    private double attritionRate;       // percentage
    private long highRiskCount;         // predictions with risk_level = "HIGH"
    private double avgProbability;      // average attrition probability
}
