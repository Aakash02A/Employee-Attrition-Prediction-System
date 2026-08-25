package com.eaps.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

/**
 * Payload sent TO the FastAPI ML service's {@code POST /predict} endpoint.
 * <p>
 * Field names use PascalCase to match the Pydantic {@code EmployeeFeatures}
 * schema exactly (e.g. "Age", "BusinessTravel", "MonthlyIncome").
 */
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MlServiceRequest {

    @JsonProperty("Age")
    private Integer age;

    @JsonProperty("DailyRate")
    private Integer dailyRate;

    @JsonProperty("DistanceFromHome")
    private Integer distanceFromHome;

    @JsonProperty("Education")
    private Integer education;

    @JsonProperty("EnvironmentSatisfaction")
    private Integer environmentSatisfaction;

    @JsonProperty("HourlyRate")
    private Integer hourlyRate;

    @JsonProperty("JobInvolvement")
    private Integer jobInvolvement;

    @JsonProperty("JobLevel")
    private Integer jobLevel;

    @JsonProperty("JobSatisfaction")
    private Integer jobSatisfaction;

    @JsonProperty("MonthlyIncome")
    private Integer monthlyIncome;

    @JsonProperty("MonthlyRate")
    private Integer monthlyRate;

    @JsonProperty("NumCompaniesWorked")
    private Integer numCompaniesWorked;

    @JsonProperty("PercentSalaryHike")
    private Integer percentSalaryHike;

    @JsonProperty("PerformanceRating")
    private Integer performanceRating;

    @JsonProperty("RelationshipSatisfaction")
    private Integer relationshipSatisfaction;

    @JsonProperty("StockOptionLevel")
    private Integer stockOptionLevel;

    @JsonProperty("TotalWorkingYears")
    private Integer totalWorkingYears;

    @JsonProperty("TrainingTimesLastYear")
    private Integer trainingTimesLastYear;

    @JsonProperty("WorkLifeBalance")
    private Integer workLifeBalance;

    @JsonProperty("YearsAtCompany")
    private Integer yearsAtCompany;

    @JsonProperty("YearsInCurrentRole")
    private Integer yearsInCurrentRole;

    @JsonProperty("YearsSinceLastPromotion")
    private Integer yearsSinceLastPromotion;

    @JsonProperty("YearsWithCurrManager")
    private Integer yearsWithCurrManager;

    // Categorical fields
    @JsonProperty("BusinessTravel")
    private String businessTravel;

    @JsonProperty("Department")
    private String department;

    @JsonProperty("EducationField")
    private String educationField;

    @JsonProperty("Gender")
    private String gender;

    @JsonProperty("JobRole")
    private String jobRole;

    @JsonProperty("MaritalStatus")
    private String maritalStatus;

    @JsonProperty("OverTime")
    private String overTime;
}
