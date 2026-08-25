package com.eaps.backend.dto;

import jakarta.validation.constraints.*;
import lombok.*;

/**
 * Request body for creating or updating an employee.
 * Field constraints mirror the ML model's expected ranges.
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EmployeeRequest {

    // Personal
    @NotNull @Min(18) @Max(60)
    private Integer age;

    @NotBlank
    private String gender;

    @NotBlank
    private String maritalStatus;

    @NotNull @Min(0) @Max(50)
    private Integer distanceFromHome;

    @NotNull @Min(1) @Max(5)
    private Integer education;

    @NotBlank
    private String educationField;

    // Job — pass department name and job role title; service resolves FK IDs
    @NotBlank
    private String department;

    @NotBlank
    private String jobRole;

    @NotNull @Min(1) @Max(5)
    private Integer jobLevel;

    @NotNull @Min(1) @Max(4)
    private Integer jobInvolvement;

    @NotNull @Min(1) @Max(4)
    private Integer jobSatisfaction;

    @NotBlank
    private String businessTravel;

    @NotBlank
    private String overTime;

    // Compensation
    @NotNull @Min(100) @Max(1500)
    private Integer dailyRate;

    @NotNull @Min(20) @Max(110)
    private Integer hourlyRate;

    @NotNull @Min(1000) @Max(25000)
    private Integer monthlyIncome;

    @NotNull @Min(2000) @Max(27000)
    private Integer monthlyRate;

    @NotNull @Min(10) @Max(25)
    private Integer percentSalaryHike;

    @NotNull @Min(0) @Max(3)
    private Integer stockOptionLevel;

    // Performance & satisfaction
    @NotNull @Min(1) @Max(4)
    private Integer performanceRating;

    @NotNull @Min(1) @Max(4)
    private Integer environmentSatisfaction;

    @NotNull @Min(1) @Max(4)
    private Integer relationshipSatisfaction;

    @NotNull @Min(1) @Max(4)
    private Integer workLifeBalance;

    // Experience
    @NotNull @Min(0) @Max(45)
    private Integer totalWorkingYears;

    @NotNull @Min(0) @Max(10)
    private Integer numCompaniesWorked;

    @NotNull @Min(0) @Max(6)
    private Integer trainingTimesLastYear;

    @NotNull @Min(0) @Max(45)
    private Integer yearsAtCompany;

    @NotNull @Min(0) @Max(20)
    private Integer yearsInCurrentRole;

    @NotNull @Min(0) @Max(15)
    private Integer yearsSinceLastPromotion;

    @NotNull @Min(0) @Max(20)
    private Integer yearsWithCurrManager;
}
