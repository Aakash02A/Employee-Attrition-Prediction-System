package com.eaps.backend.service;

import com.eaps.backend.dto.MlServiceRequest;
import com.eaps.backend.dto.MlServiceResponse;
import com.eaps.backend.dto.PredictionResponse;
import com.eaps.backend.model.AppUser;
import com.eaps.backend.model.Department;
import com.eaps.backend.model.Employee;
import com.eaps.backend.model.JobRole;
import com.eaps.backend.model.Prediction;
import com.eaps.backend.repository.AppUserRepository;
import com.eaps.backend.repository.EmployeeRepository;
import com.eaps.backend.repository.PredictionRepository;
import jakarta.persistence.EntityNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PredictionServiceTest {

    @Mock
    private EmployeeRepository employeeRepository;
    @Mock
    private PredictionRepository predictionRepository;
    @Mock
    private AppUserRepository appUserRepository;
    @Mock
    private MlServiceClient mlServiceClient;

    @InjectMocks
    private PredictionService predictionService;

    private Employee sampleEmployee;
    private AppUser sampleUser;
    private Prediction samplePrediction;

    @BeforeEach
    void setUp() {
        Department rdDept = Department.builder().id(1L).name("Research & Development").build();
        JobRole rsRole = JobRole.builder().id(1L).title("Research Scientist").build();

        sampleEmployee = Employee.builder()
                .id(1L)
                .empCode("EMP001")
                .age(35)
                .gender("Male")
                .maritalStatus("Married")
                .distanceFromHome(5)
                .education(3)
                .educationField("Life Sciences")
                .department(rdDept)
                .jobRole(rsRole)
                .jobLevel(2)
                .jobInvolvement(3)
                .jobSatisfaction(3)
                .businessTravel("Travel_Rarely")
                .overTime("No")
                .dailyRate(800)
                .hourlyRate(65)
                .monthlyIncome(5500)
                .monthlyRate(12000)
                .percentSalaryHike(14)
                .stockOptionLevel(1)
                .performanceRating(3)
                .environmentSatisfaction(3)
                .relationshipSatisfaction(3)
                .workLifeBalance(3)
                .totalWorkingYears(10)
                .numCompaniesWorked(2)
                .trainingTimesLastYear(3)
                .yearsAtCompany(8)
                .yearsInCurrentRole(5)
                .yearsSinceLastPromotion(1)
                .yearsWithCurrManager(6)
                .build();

        sampleUser = AppUser.builder()
                .id(1L)
                .username("admin")
                .email("admin@eaps.com")
                .build();

        samplePrediction = Prediction.builder()
                .id(100L)
                .employee(sampleEmployee)
                .prediction("STAY")
                .probability(0.2259)
                .riskLevel("LOW")
                .modelVersion("random_forest_tuned_v2_2026-08-25")
                .decisionThreshold(0.4936)
                .requestedBy(sampleUser)
                .createdAt(LocalDateTime.now())
                .build();
    }

    @Test
    void testPredictAttrition_Success() {
        MlServiceResponse mlResponse = MlServiceResponse.builder()
                .prediction("STAY")
                .probability(0.2259)
                .riskLevel("LOW")
                .modelVersion("random_forest_tuned_v2_2026-08-25")
                .decisionThreshold(0.4936)
                .build();

        when(employeeRepository.findById(1L)).thenReturn(Optional.of(sampleEmployee));
        when(appUserRepository.findByUsername("admin")).thenReturn(Optional.of(sampleUser));
        when(mlServiceClient.predict(any(MlServiceRequest.class))).thenReturn(mlResponse);
        when(predictionRepository.save(any(Prediction.class))).thenReturn(samplePrediction);

        PredictionResponse response = predictionService.predictAttrition(1L, "admin");

        assertNotNull(response);
        assertEquals("EMP001", response.getEmpCode());
        assertEquals("STAY", response.getPrediction());
        assertEquals(0.2259, response.getProbability());
        assertEquals("LOW", response.getRiskLevel());
        assertEquals("random_forest_tuned_v2_2026-08-25", response.getModelVersion());

        verify(mlServiceClient, times(1)).predict(any(MlServiceRequest.class));
        verify(predictionRepository, times(1)).save(any(Prediction.class));
    }

    @Test
    void testPredictAttrition_EmployeeNotFound() {
        when(employeeRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(EntityNotFoundException.class, () -> predictionService.predictAttrition(999L, "admin"));
        verify(mlServiceClient, never()).predict(any());
        verify(predictionRepository, never()).save(any());
    }

    @Test
    void testGetAllPredictions() {
        when(predictionRepository.findAllByOrderByCreatedAtDesc()).thenReturn(List.of(samplePrediction));

        List<PredictionResponse> results = predictionService.getAllPredictions();

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("EMP001", results.get(0).getEmpCode());
    }

    @Test
    void testGetPredictionsByEmployee() {
        when(predictionRepository.findByEmployeeIdOrderByCreatedAtDesc(1L)).thenReturn(List.of(samplePrediction));

        List<PredictionResponse> results = predictionService.getPredictionsByEmployee(1L);

        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("EMP001", results.get(0).getEmpCode());
    }

    @Test
    void testGetHighRiskEmployees() {
        when(predictionRepository.findLatestPredictionsByRiskLevel("HIGH")).thenReturn(List.of(samplePrediction));

        List<PredictionResponse> results = predictionService.getHighRiskEmployees();

        assertNotNull(results);
        assertEquals(1, results.size());
    }
}
