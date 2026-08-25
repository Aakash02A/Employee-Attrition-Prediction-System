package com.eaps.backend.service;

import com.eaps.backend.dto.*;
import com.eaps.backend.model.AppUser;
import com.eaps.backend.model.Employee;
import com.eaps.backend.model.Prediction;
import com.eaps.backend.repository.AppUserRepository;
import com.eaps.backend.repository.EmployeeRepository;
import com.eaps.backend.repository.PredictionRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Orchestrates the prediction workflow:
 * <ol>
 *   <li>Fetch employee from DB</li>
 *   <li>Map employee fields → ML request (matching FastAPI's EmployeeFeatures)</li>
 *   <li>Call FastAPI via {@link MlServiceClient}</li>
 *   <li>Save prediction to DB</li>
 *   <li>Return result</li>
 * </ol>
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PredictionService {

    private final EmployeeRepository employeeRepository;
    private final PredictionRepository predictionRepository;
    private final AppUserRepository appUserRepository;
    private final MlServiceClient mlServiceClient;

    /**
     * Run an attrition prediction for the given employee.
     *
     * @param employeeId  the employee to predict
     * @param requestedByUsername  the username of the user requesting the prediction
     * @return the prediction result
     */
    @Transactional
    public PredictionResponse predictAttrition(Long employeeId, String requestedByUsername) {
        Employee employee = employeeRepository.findById(employeeId)
                .orElseThrow(() -> new EntityNotFoundException("Employee not found with id: " + employeeId));

        // For now, during Phase 7, use a default admin user if auth isn't wired yet
        AppUser requestedBy = appUserRepository.findByUsername(requestedByUsername)
                .orElseGet(() -> appUserRepository.findByUsername("admin")
                        .orElseThrow(() -> new EntityNotFoundException("No admin user found. Run schema.sql to seed the database.")));

        // Map Employee → MlServiceRequest (PascalCase fields matching the Pydantic schema)
        MlServiceRequest mlRequest = MlServiceRequest.builder()
                .age(employee.getAge())
                .dailyRate(employee.getDailyRate())
                .distanceFromHome(employee.getDistanceFromHome())
                .education(employee.getEducation())
                .environmentSatisfaction(employee.getEnvironmentSatisfaction())
                .hourlyRate(employee.getHourlyRate())
                .jobInvolvement(employee.getJobInvolvement())
                .jobLevel(employee.getJobLevel())
                .jobSatisfaction(employee.getJobSatisfaction())
                .monthlyIncome(employee.getMonthlyIncome())
                .monthlyRate(employee.getMonthlyRate())
                .numCompaniesWorked(employee.getNumCompaniesWorked())
                .percentSalaryHike(employee.getPercentSalaryHike())
                .performanceRating(employee.getPerformanceRating())
                .relationshipSatisfaction(employee.getRelationshipSatisfaction())
                .stockOptionLevel(employee.getStockOptionLevel())
                .totalWorkingYears(employee.getTotalWorkingYears())
                .trainingTimesLastYear(employee.getTrainingTimesLastYear())
                .workLifeBalance(employee.getWorkLifeBalance())
                .yearsAtCompany(employee.getYearsAtCompany())
                .yearsInCurrentRole(employee.getYearsInCurrentRole())
                .yearsSinceLastPromotion(employee.getYearsSinceLastPromotion())
                .yearsWithCurrManager(employee.getYearsWithCurrManager())
                // Categorical fields
                .businessTravel(employee.getBusinessTravel())
                .department(employee.getDepartment().getName())
                .educationField(employee.getEducationField())
                .gender(employee.getGender())
                .jobRole(employee.getJobRole().getTitle())
                .maritalStatus(employee.getMaritalStatus())
                .overTime(employee.getOverTime())
                .build();

        // Call FastAPI ML service
        MlServiceResponse mlResponse = mlServiceClient.predict(mlRequest);

        // Persist prediction
        Prediction prediction = Prediction.builder()
                .employee(employee)
                .prediction(mlResponse.getPrediction())
                .probability(mlResponse.getProbability())
                .riskLevel(mlResponse.getRiskLevel())
                .modelVersion(mlResponse.getModelVersion())
                .decisionThreshold(mlResponse.getDecisionThreshold())
                .requestedBy(requestedBy)
                .build();

        Prediction saved = predictionRepository.save(prediction);
        log.info("Prediction saved: id={}, employee={}, result={}, risk={}",
                saved.getId(), employee.getEmpCode(), saved.getPrediction(), saved.getRiskLevel());

        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<PredictionResponse> getAllPredictions() {
        return predictionRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<PredictionResponse> getPredictionsByEmployee(Long employeeId) {
        return predictionRepository.findByEmployeeIdOrderByCreatedAtDesc(employeeId).stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<PredictionResponse> getHighRiskEmployees() {
        return predictionRepository.findLatestPredictionsByRiskLevel("HIGH").stream()
                .map(this::toResponse)
                .toList();
    }

    // ── Helper: Entity → Response DTO ─────────────────────────

    private PredictionResponse toResponse(Prediction p) {
        return PredictionResponse.builder()
                .id(p.getId())
                .employeeId(p.getEmployee().getId())
                .empCode(p.getEmployee().getEmpCode())
                .employeeDepartment(p.getEmployee().getDepartment().getName())
                .employeeJobRole(p.getEmployee().getJobRole().getTitle())
                .prediction(p.getPrediction())
                .probability(p.getProbability())
                .riskLevel(p.getRiskLevel())
                .modelVersion(p.getModelVersion())
                .decisionThreshold(p.getDecisionThreshold())
                .requestedBy(p.getRequestedBy().getUsername())
                .createdAt(p.getCreatedAt())
                .build();
    }
}
