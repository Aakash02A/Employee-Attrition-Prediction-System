package com.eaps.backend.controller;

import com.eaps.backend.dto.EmployeeRequest;
import com.eaps.backend.dto.EmployeeResponse;
import com.eaps.backend.exception.GlobalExceptionHandler;
import com.eaps.backend.service.EmployeeService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.EntityNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class EmployeeControllerTest {

    private MockMvc mockMvc;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Mock
    private EmployeeService employeeService;

    @InjectMocks
    private EmployeeController employeeController;

    private EmployeeResponse sampleResponse;
    private EmployeeRequest sampleRequest;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(employeeController)
                .setControllerAdvice(new GlobalExceptionHandler())
                .build();

        sampleResponse = EmployeeResponse.builder()
                .id(1L)
                .empCode("EMP001")
                .age(35)
                .department("Research & Development")
                .jobRole("Research Scientist")
                .monthlyIncome(5500)
                .build();

        sampleRequest = EmployeeRequest.builder()
                .age(35)
                .gender("Male")
                .maritalStatus("Married")
                .distanceFromHome(5)
                .education(3)
                .educationField("Life Sciences")
                .department("Research & Development")
                .jobRole("Research Scientist")
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
    }

    @Test
    void testGetAllEmployees() throws Exception {
        when(employeeService.getAllEmployees()).thenReturn(List.of(sampleResponse));

        mockMvc.perform(get("/api/employees"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].empCode").value("EMP001"));

        verify(employeeService, times(1)).getAllEmployees();
    }

    @Test
    void testGetEmployeeById_Success() throws Exception {
        when(employeeService.getEmployeeById(1L)).thenReturn(sampleResponse);

        mockMvc.perform(get("/api/employees/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.empCode").value("EMP001"));
    }

    @Test
    void testGetEmployeeById_NotFound() throws Exception {
        when(employeeService.getEmployeeById(999L)).thenThrow(new EntityNotFoundException("Employee not found with id: 999"));

        mockMvc.perform(get("/api/employees/999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error").value("Not Found"));
    }

    @Test
    void testCreateEmployee_Success() throws Exception {
        when(employeeService.createEmployee(any(EmployeeRequest.class))).thenReturn(sampleResponse);

        mockMvc.perform(post("/api/employees")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(sampleRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.empCode").value("EMP001"));

        verify(employeeService, times(1)).createEmployee(any(EmployeeRequest.class));
    }

    @Test
    void testCreateEmployee_ValidationFailure() throws Exception {
        EmployeeRequest invalidRequest = new EmployeeRequest(); // missing all required fields

        mockMvc.perform(post("/api/employees")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation Failed"));

        verify(employeeService, never()).createEmployee(any());
    }

    @Test
    void testUpdateEmployee_Success() throws Exception {
        when(employeeService.updateEmployee(eq(1L), any(EmployeeRequest.class))).thenReturn(sampleResponse);

        mockMvc.perform(put("/api/employees/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(sampleRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.empCode").value("EMP001"));

        verify(employeeService, times(1)).updateEmployee(eq(1L), any(EmployeeRequest.class));
    }

    @Test
    void testDeleteEmployee_Success() throws Exception {
        doNothing().when(employeeService).deleteEmployee(1L);

        mockMvc.perform(delete("/api/employees/1"))
                .andExpect(status().isNoContent());

        verify(employeeService, times(1)).deleteEmployee(1L);
    }
}
