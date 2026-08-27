package com.eaps.backend.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * JPA entity for the {@code employees} table.
 * <p>
 * Every column in this entity maps to a feature expected by the ML model
 * (see {@code ml-service/app/schemas.py → EmployeeFeatures}).
 * When predicting, the service maps these fields into the ML request payload.
 */
@Entity
@Table(name = "employees")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "employee_id")
    private Long id;

    @Column(name = "emp_code", nullable = false, unique = true, length = 20)
    private String empCode;

    // ── Personal ──────────────────────────────────────────────

    @Column(nullable = false)
    private Integer age;

    @Column(nullable = false, length = 10)
    private String gender; // "Male" / "Female"

    @Column(name = "marital_status", nullable = false, length = 10)
    private String maritalStatus; // "Single" / "Married" / "Divorced"

    @Column(name = "distance_from_home", nullable = false)
    private Integer distanceFromHome;

    @Column(nullable = false)
    private Integer education; // 1–5

    @Column(name = "education_field", nullable = false, length = 50)
    private String educationField;

    // ── Job ───────────────────────────────────────────────────

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id", nullable = false)
    private Department department;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_role_id", nullable = false)
    private JobRole jobRole;

    @Column(name = "job_level", nullable = false)
    private Integer jobLevel;

    @Column(name = "job_involvement", nullable = false)
    private Integer jobInvolvement;

    @Column(name = "job_satisfaction", nullable = false)
    private Integer jobSatisfaction;

    @Column(name = "business_travel", nullable = false, length = 25)
    private String businessTravel; // "Non-Travel" / "Travel_Frequently" / "Travel_Rarely"

    @Column(name = "over_time", nullable = false, length = 5)
    private String overTime; // "Yes" / "No"

    // ── Compensation ──────────────────────────────────────────

    @Column(name = "daily_rate", nullable = false)
    private Integer dailyRate;

    @Column(name = "hourly_rate", nullable = false)
    private Integer hourlyRate;

    @Column(name = "monthly_income", nullable = false)
    private Integer monthlyIncome;

    @Column(name = "monthly_rate", nullable = false)
    private Integer monthlyRate;

    @Column(name = "percent_salary_hike", nullable = false)
    private Integer percentSalaryHike;

    @Column(name = "stock_option_level", nullable = false)
    private Integer stockOptionLevel;

    // ── Performance & satisfaction ────────────────────────────

    @Column(name = "performance_rating", nullable = false)
    private Integer performanceRating;

    @Column(name = "environment_satisfaction", nullable = false)
    private Integer environmentSatisfaction;

    @Column(name = "relationship_satisfaction", nullable = false)
    private Integer relationshipSatisfaction;

    @Column(name = "work_life_balance", nullable = false)
    private Integer workLifeBalance;

    // ── Experience ────────────────────────────────────────────

    @Column(name = "total_working_years", nullable = false)
    private Integer totalWorkingYears;

    @Column(name = "num_companies_worked", nullable = false)
    private Integer numCompaniesWorked;

    @Column(name = "training_times_last_year", nullable = false)
    private Integer trainingTimesLastYear;

    @Column(name = "years_at_company", nullable = false)
    private Integer yearsAtCompany;

    @Column(name = "years_in_current_role", nullable = false)
    private Integer yearsInCurrentRole;

    @Column(name = "years_since_last_promotion", nullable = false)
    private Integer yearsSinceLastPromotion;

    @Column(name = "years_with_curr_manager", nullable = false)
    private Integer yearsWithCurrManager;

    // ── Timestamps ────────────────────────────────────────────

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
