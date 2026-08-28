package com.eaps.backend.service;

import com.eaps.backend.dto.EmployeeRequest;
import com.eaps.backend.dto.EmployeeResponse;
import com.eaps.backend.model.Department;
import com.eaps.backend.model.Employee;
import com.eaps.backend.model.JobRole;
import com.eaps.backend.repository.DepartmentRepository;
import com.eaps.backend.repository.EmployeeRepository;
import com.eaps.backend.repository.JobRoleRepository;
import com.eaps.backend.repository.PredictionRepository;
import jakarta.persistence.EntityNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EmployeeServiceTest {

    @Mock
    private EmployeeRepository employeeRepository;
    @Mock
    private DepartmentRepository departmentRepository;
    @Mock
    private JobRoleRepository jobRoleRepository;
    @Mock
    private PredictionRepository predictionRepository;

    @InjectMocks
    private EmployeeService employeeService;

    private Department salesDept;
    private JobRole salesExecRole;
    private Employee sampleEmployee;
    private EmployeeRequest sampleRequest;

    @BeforeEach
    void setUp() {
        salesDept = Department.builder().id(1L).name("Sales").build();
        salesExecRole = JobRole.builder().id(1L).title("Sales Executive").build();

        sampleEmployee = Employee.builder()
                .id(10L)
                .empCode("EMP-1001")
                .age(32)
                .gender("Female")
                .maritalStatus("Single")
                .distanceFromHome(5)
                .education(3)
                .educationField("Life Sciences")
                .department(salesDept)
                .jobRole(salesExecRole)
                .jobLevel(2)
                .jobInvolvement(3)
                .jobSatisfaction(3)
                .businessTravel("Travel_Rarely")
                .overTime("No")
                .dailyRate(800)
                .hourlyRate(65)
                .monthlyIncome(5500)
                .monthlyRate(14000)
                .percentSalaryHike(14)
                .stockOptionLevel(1)
                .performanceRating(3)
                .environmentSatisfaction(3)
                .relationshipSatisfaction(3)
                .workLifeBalance(3)
                .totalWorkingYears(8)
                .numCompaniesWorked(2)
                .trainingTimesLastYear(3)
                .yearsAtCompany(5)
                .yearsInCurrentRole(3)
                .yearsSinceLastPromotion(1)
                .yearsWithCurrManager(3)
                .build();

        sampleRequest = EmployeeRequest.builder()
                .age(32)
                .gender("Female")
                .maritalStatus("Single")
                .distanceFromHome(5)
                .education(3)
                .educationField("Life Sciences")
                .department("Sales")
                .jobRole("Sales Executive")
                .jobLevel(2)
                .jobInvolvement(3)
                .jobSatisfaction(3)
                .businessTravel("Travel_Rarely")
                .overTime("No")
                .dailyRate(800)
                .hourlyRate(65)
                .monthlyIncome(5500)
                .monthlyRate(14000)
                .percentSalaryHike(14)
                .stockOptionLevel(1)
                .performanceRating(3)
                .environmentSatisfaction(3)
                .relationshipSatisfaction(3)
                .workLifeBalance(3)
                .totalWorkingYears(8)
                .numCompaniesWorked(2)
                .trainingTimesLastYear(3)
                .yearsAtCompany(5)
                .yearsInCurrentRole(3)
                .yearsSinceLastPromotion(1)
                .yearsWithCurrManager(3)
                .build();
    }

    @Test
    void testGetAllEmployees() {
        when(employeeRepository.findAll()).thenReturn(List.of(sampleEmployee));
        when(predictionRepository.findFirstByEmployeeIdOrderByCreatedAtDesc(10L)).thenReturn(Optional.empty());

        List<EmployeeResponse> responses = employeeService.getAllEmployees();

        assertNotNull(responses);
        assertEquals(1, responses.size());
        assertEquals("EMP-1001", responses.get(0).getEmpCode());
        assertEquals("Sales", responses.get(0).getDepartment());
        verify(employeeRepository, times(1)).findAll();
    }

    @Test
    void testGetEmployeeById_Success() {
        when(employeeRepository.findById(10L)).thenReturn(Optional.of(sampleEmployee));
        when(predictionRepository.findFirstByEmployeeIdOrderByCreatedAtDesc(10L)).thenReturn(Optional.empty());

        EmployeeResponse response = employeeService.getEmployeeById(10L);

        assertNotNull(response);
        assertEquals(10L, response.getId());
        assertEquals("EMP-1001", response.getEmpCode());
    }

    @Test
    void testGetEmployeeById_NotFound() {
        when(employeeRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(EntityNotFoundException.class, () -> employeeService.getEmployeeById(999L));
    }

    @Test
    void testCreateEmployee_Success() {
        when(departmentRepository.findByName("Sales")).thenReturn(Optional.of(salesDept));
        when(jobRoleRepository.findByTitle("Sales Executive")).thenReturn(Optional.of(salesExecRole));
        when(employeeRepository.existsByEmpCode(anyString())).thenReturn(false);
        when(employeeRepository.save(any(Employee.class))).thenAnswer(invocation -> {
            Employee e = invocation.getArgument(0);
            e.setId(101L);
            return e;
        });

        EmployeeResponse response = employeeService.createEmployee(sampleRequest);

        assertNotNull(response);
        assertEquals(101L, response.getId());
        assertEquals("Sales", response.getDepartment());
        assertEquals("Sales Executive", response.getJobRole());
        verify(employeeRepository, times(1)).save(any(Employee.class));
    }

    @Test
    void testCreateEmployee_DepartmentNotFound() {
        when(departmentRepository.findByName("Sales")).thenReturn(Optional.empty());

        assertThrows(EntityNotFoundException.class, () -> employeeService.createEmployee(sampleRequest));
        verify(employeeRepository, never()).save(any());
    }

    @Test
    void testUpdateEmployee_Success() {
        when(employeeRepository.findById(10L)).thenReturn(Optional.of(sampleEmployee));
        when(departmentRepository.findByName("Sales")).thenReturn(Optional.of(salesDept));
        when(jobRoleRepository.findByTitle("Sales Executive")).thenReturn(Optional.of(salesExecRole));
        when(employeeRepository.save(any(Employee.class))).thenReturn(sampleEmployee);

        sampleRequest.setMonthlyIncome(8000);
        EmployeeResponse response = employeeService.updateEmployee(10L, sampleRequest);

        assertNotNull(response);
        assertEquals(8000, response.getMonthlyIncome());
        verify(employeeRepository, times(1)).save(sampleEmployee);
    }

    @Test
    void testDeleteEmployee_Success() {
        when(employeeRepository.existsById(10L)).thenReturn(true);
        doNothing().when(employeeRepository).deleteById(10L);

        assertDoesNotThrow(() -> employeeService.deleteEmployee(10L));
        verify(employeeRepository, times(1)).deleteById(10L);
    }

    @Test
    void testDeleteEmployee_NotFound() {
        when(employeeRepository.existsById(999L)).thenReturn(false);

        assertThrows(EntityNotFoundException.class, () -> employeeService.deleteEmployee(999L));
        verify(employeeRepository, never()).deleteById(anyLong());
    }
}
