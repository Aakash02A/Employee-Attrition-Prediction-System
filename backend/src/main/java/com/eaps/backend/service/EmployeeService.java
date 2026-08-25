package com.eaps.backend.service;

import com.eaps.backend.dto.EmployeeRequest;
import com.eaps.backend.dto.EmployeeResponse;
import com.eaps.backend.model.Department;
import com.eaps.backend.model.Employee;
import com.eaps.backend.model.JobRole;
import com.eaps.backend.model.Prediction;
import com.eaps.backend.repository.DepartmentRepository;
import com.eaps.backend.repository.EmployeeRepository;
import com.eaps.backend.repository.JobRoleRepository;
import com.eaps.backend.repository.PredictionRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;
    private final JobRoleRepository jobRoleRepository;
    private final PredictionRepository predictionRepository;

    // Simple auto-incrementing employee code generator
    private final AtomicLong empCodeCounter = new AtomicLong(1000);

    @Transactional(readOnly = true)
    public List<EmployeeResponse> getAllEmployees() {
        return employeeRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public EmployeeResponse getEmployeeById(Long id) {
        Employee employee = employeeRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Employee not found with id: " + id));
        return toResponse(employee);
    }

    @Transactional
    public EmployeeResponse createEmployee(EmployeeRequest request) {
        Department department = departmentRepository.findByName(request.getDepartment())
                .orElseThrow(() -> new EntityNotFoundException("Department not found: " + request.getDepartment()));

        JobRole jobRole = jobRoleRepository.findByTitle(request.getJobRole())
                .orElseThrow(() -> new EntityNotFoundException("Job role not found: " + request.getJobRole()));

        // Generate a unique employee code
        String empCode = "EMP-" + empCodeCounter.incrementAndGet();
        while (employeeRepository.existsByEmpCode(empCode)) {
            empCode = "EMP-" + empCodeCounter.incrementAndGet();
        }

        Employee employee = Employee.builder()
                .empCode(empCode)
                .age(request.getAge())
                .gender(request.getGender())
                .maritalStatus(request.getMaritalStatus())
                .distanceFromHome(request.getDistanceFromHome())
                .education(request.getEducation())
                .educationField(request.getEducationField())
                .department(department)
                .jobRole(jobRole)
                .jobLevel(request.getJobLevel())
                .jobInvolvement(request.getJobInvolvement())
                .jobSatisfaction(request.getJobSatisfaction())
                .businessTravel(request.getBusinessTravel())
                .overTime(request.getOverTime())
                .dailyRate(request.getDailyRate())
                .hourlyRate(request.getHourlyRate())
                .monthlyIncome(request.getMonthlyIncome())
                .monthlyRate(request.getMonthlyRate())
                .percentSalaryHike(request.getPercentSalaryHike())
                .stockOptionLevel(request.getStockOptionLevel())
                .performanceRating(request.getPerformanceRating())
                .environmentSatisfaction(request.getEnvironmentSatisfaction())
                .relationshipSatisfaction(request.getRelationshipSatisfaction())
                .workLifeBalance(request.getWorkLifeBalance())
                .totalWorkingYears(request.getTotalWorkingYears())
                .numCompaniesWorked(request.getNumCompaniesWorked())
                .trainingTimesLastYear(request.getTrainingTimesLastYear())
                .yearsAtCompany(request.getYearsAtCompany())
                .yearsInCurrentRole(request.getYearsInCurrentRole())
                .yearsSinceLastPromotion(request.getYearsSinceLastPromotion())
                .yearsWithCurrManager(request.getYearsWithCurrManager())
                .build();

        Employee saved = employeeRepository.save(employee);
        log.info("Created employee: {} ({})", saved.getEmpCode(), saved.getId());
        return toResponse(saved);
    }

    @Transactional
    public EmployeeResponse updateEmployee(Long id, EmployeeRequest request) {
        Employee employee = employeeRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Employee not found with id: " + id));

        Department department = departmentRepository.findByName(request.getDepartment())
                .orElseThrow(() -> new EntityNotFoundException("Department not found: " + request.getDepartment()));

        JobRole jobRole = jobRoleRepository.findByTitle(request.getJobRole())
                .orElseThrow(() -> new EntityNotFoundException("Job role not found: " + request.getJobRole()));

        // Update all fields
        employee.setAge(request.getAge());
        employee.setGender(request.getGender());
        employee.setMaritalStatus(request.getMaritalStatus());
        employee.setDistanceFromHome(request.getDistanceFromHome());
        employee.setEducation(request.getEducation());
        employee.setEducationField(request.getEducationField());
        employee.setDepartment(department);
        employee.setJobRole(jobRole);
        employee.setJobLevel(request.getJobLevel());
        employee.setJobInvolvement(request.getJobInvolvement());
        employee.setJobSatisfaction(request.getJobSatisfaction());
        employee.setBusinessTravel(request.getBusinessTravel());
        employee.setOverTime(request.getOverTime());
        employee.setDailyRate(request.getDailyRate());
        employee.setHourlyRate(request.getHourlyRate());
        employee.setMonthlyIncome(request.getMonthlyIncome());
        employee.setMonthlyRate(request.getMonthlyRate());
        employee.setPercentSalaryHike(request.getPercentSalaryHike());
        employee.setStockOptionLevel(request.getStockOptionLevel());
        employee.setPerformanceRating(request.getPerformanceRating());
        employee.setEnvironmentSatisfaction(request.getEnvironmentSatisfaction());
        employee.setRelationshipSatisfaction(request.getRelationshipSatisfaction());
        employee.setWorkLifeBalance(request.getWorkLifeBalance());
        employee.setTotalWorkingYears(request.getTotalWorkingYears());
        employee.setNumCompaniesWorked(request.getNumCompaniesWorked());
        employee.setTrainingTimesLastYear(request.getTrainingTimesLastYear());
        employee.setYearsAtCompany(request.getYearsAtCompany());
        employee.setYearsInCurrentRole(request.getYearsInCurrentRole());
        employee.setYearsSinceLastPromotion(request.getYearsSinceLastPromotion());
        employee.setYearsWithCurrManager(request.getYearsWithCurrManager());

        Employee saved = employeeRepository.save(employee);
        log.info("Updated employee: {} ({})", saved.getEmpCode(), saved.getId());
        return toResponse(saved);
    }

    @Transactional
    public void deleteEmployee(Long id) {
        if (!employeeRepository.existsById(id)) {
            throw new EntityNotFoundException("Employee not found with id: " + id);
        }
        employeeRepository.deleteById(id);
        log.info("Deleted employee with id: {}", id);
    }

    // ── Helper: Entity → Response DTO ─────────────────────────

    private EmployeeResponse toResponse(Employee e) {
        EmployeeResponse.EmployeeResponseBuilder builder = EmployeeResponse.builder()
                .id(e.getId())
                .empCode(e.getEmpCode())
                .age(e.getAge())
                .gender(e.getGender())
                .maritalStatus(e.getMaritalStatus())
                .distanceFromHome(e.getDistanceFromHome())
                .education(e.getEducation())
                .educationField(e.getEducationField())
                .department(e.getDepartment().getName())
                .jobRole(e.getJobRole().getTitle())
                .jobLevel(e.getJobLevel())
                .jobInvolvement(e.getJobInvolvement())
                .jobSatisfaction(e.getJobSatisfaction())
                .businessTravel(e.getBusinessTravel())
                .overTime(e.getOverTime())
                .dailyRate(e.getDailyRate())
                .hourlyRate(e.getHourlyRate())
                .monthlyIncome(e.getMonthlyIncome())
                .monthlyRate(e.getMonthlyRate())
                .percentSalaryHike(e.getPercentSalaryHike())
                .stockOptionLevel(e.getStockOptionLevel())
                .performanceRating(e.getPerformanceRating())
                .environmentSatisfaction(e.getEnvironmentSatisfaction())
                .relationshipSatisfaction(e.getRelationshipSatisfaction())
                .workLifeBalance(e.getWorkLifeBalance())
                .totalWorkingYears(e.getTotalWorkingYears())
                .numCompaniesWorked(e.getNumCompaniesWorked())
                .trainingTimesLastYear(e.getTrainingTimesLastYear())
                .yearsAtCompany(e.getYearsAtCompany())
                .yearsInCurrentRole(e.getYearsInCurrentRole())
                .yearsSinceLastPromotion(e.getYearsSinceLastPromotion())
                .yearsWithCurrManager(e.getYearsWithCurrManager())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt());

        // Attach latest prediction if one exists
        predictionRepository.findFirstByEmployeeIdOrderByCreatedAtDesc(e.getId())
                .ifPresent(p -> {
                    builder.latestPrediction(p.getPrediction());
                    builder.latestProbability(p.getProbability());
                    builder.latestRiskLevel(p.getRiskLevel());
                    builder.latestPredictionDate(p.getCreatedAt());
                });

        return builder.build();
    }
}
