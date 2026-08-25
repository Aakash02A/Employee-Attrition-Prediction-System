package com.eaps.backend.dto;

import lombok.*;

import java.time.LocalDateTime;

/**
 * Response body when returning employee data to the frontend.
 * Includes the latest prediction (if one exists) for quick risk display.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EmployeeResponse {

    private Long id;
    private String empCode;

    // Personal
    private Integer age;
    private String gender;
    private String maritalStatus;
    private Integer distanceFromHome;
    private Integer education;
    private String educationField;

    // Job
    private String department;
    private String jobRole;
    private Integer jobLevel;
    private Integer jobInvolvement;
    private Integer jobSatisfaction;
    private String businessTravel;
    private String overTime;

    // Compensation
    private Integer dailyRate;
    private Integer hourlyRate;
    private Integer monthlyIncome;
    private Integer monthlyRate;
    private Integer percentSalaryHike;
    private Integer stockOptionLevel;

    // Performance & satisfaction
    private Integer performanceRating;
    private Integer environmentSatisfaction;
    private Integer relationshipSatisfaction;
    private Integer workLifeBalance;

    // Experience
    private Integer totalWorkingYears;
    private Integer numCompaniesWorked;
    private Integer trainingTimesLastYear;
    private Integer yearsAtCompany;
    private Integer yearsInCurrentRole;
    private Integer yearsSinceLastPromotion;
    private Integer yearsWithCurrManager;

    // Latest prediction (nullable — may not have been predicted yet)
    private String latestPrediction;      // "STAY" / "LEAVE"
    private Double latestProbability;
    private String latestRiskLevel;       // "LOW" / "MEDIUM" / "HIGH"
    private LocalDateTime latestPredictionDate;

    // Timestamps
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
