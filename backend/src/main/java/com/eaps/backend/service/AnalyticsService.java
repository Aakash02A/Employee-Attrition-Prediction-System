package com.eaps.backend.service;

import com.eaps.backend.dto.AnalyticsResponse;
import com.eaps.backend.dto.DashboardKpiResponse;
import com.eaps.backend.repository.EmployeeRepository;
import com.eaps.backend.repository.PredictionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Provides aggregated data for the dashboard KPI cards and analytics charts.
 */
@Service
@RequiredArgsConstructor
public class AnalyticsService {

    private final EmployeeRepository employeeRepository;
    private final PredictionRepository predictionRepository;

    /**
     * Dashboard KPI cards: total employees, attrition count/rate, high-risk, avg probability.
     */
    @Transactional(readOnly = true)
    public DashboardKpiResponse getDashboardKpis() {
        long totalEmployees = employeeRepository.count();
        long attritionCount = predictionRepository.countAttrition();
        long highRiskCount = predictionRepository.countHighRisk();
        Double avgProbability = predictionRepository.averageProbability();

        double attritionRate = totalEmployees > 0
                ? (double) attritionCount / totalEmployees * 100
                : 0.0;

        return DashboardKpiResponse.builder()
                .totalEmployees(totalEmployees)
                .attritionCount(attritionCount)
                .attritionRate(Math.round(attritionRate * 100.0) / 100.0) // 2 decimal places
                .highRiskCount(highRiskCount)
                .avgProbability(avgProbability != null ? Math.round(avgProbability * 10000.0) / 100.0 : 0.0) // convert to % with 2 decimals
                .build();
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByDepartment() {
        return buildAnalyticsResponse("Attrition by Department",
                predictionRepository.countAttritionByDepartment());
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByJobRole() {
        return buildAnalyticsResponse("Attrition by Job Role",
                predictionRepository.countAttritionByJobRole());
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByAgeGroup() {
        return buildAnalyticsResponse("Attrition by Age Group",
                predictionRepository.countAttritionByAgeGroup());
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionBySalaryRange() {
        return buildAnalyticsResponse("Attrition by Salary Range",
                predictionRepository.countAttritionBySalaryRange());
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByOvertime() {
        return buildAnalyticsResponse("Attrition by Overtime",
                predictionRepository.countAttritionByOvertime());
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByJobSatisfaction() {
        List<Object[]> raw = predictionRepository.countAttritionByJobSatisfaction();
        List<String> labels = new ArrayList<>();
        List<Long> data = new ArrayList<>();

        // Map satisfaction levels to human-readable labels
        Map<Integer, String> satisfactionLabels = Map.of(
                1, "1 (Low)", 2, "2", 3, "3", 4, "4 (High)");

        for (Object[] row : raw) {
            Integer level = (Integer) row[0];
            labels.add(satisfactionLabels.getOrDefault(level, String.valueOf(level)));
            data.add((Long) row[1]);
        }

        return AnalyticsResponse.builder()
                .chartTitle("Attrition by Job Satisfaction")
                .labels(labels)
                .data(data)
                .build();
    }

    @Transactional(readOnly = true)
    public AnalyticsResponse getAttritionByYearsAtCompany() {
        return buildAnalyticsResponse("Attrition by Years at Company",
                predictionRepository.countAttritionByYearsAtCompany());
    }

    // ── Helper ────────────────────────────────────────────────

    private AnalyticsResponse buildAnalyticsResponse(String title, List<Object[]> rows) {
        List<String> labels = new ArrayList<>();
        List<Long> data = new ArrayList<>();

        for (Object[] row : rows) {
            labels.add(String.valueOf(row[0]));
            data.add((Long) row[1]);
        }

        return AnalyticsResponse.builder()
                .chartTitle(title)
                .labels(labels)
                .data(data)
                .build();
    }
}
