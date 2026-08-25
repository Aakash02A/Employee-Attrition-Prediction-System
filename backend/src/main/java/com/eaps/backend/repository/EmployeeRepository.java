package com.eaps.backend.repository;

import com.eaps.backend.model.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    Optional<Employee> findByEmpCode(String empCode);

    boolean existsByEmpCode(String empCode);

    List<Employee> findByDepartmentId(Long departmentId);

    List<Employee> findByJobRoleId(Long jobRoleId);

    // --- Analytics queries ---

    @Query("SELECT COUNT(e) FROM Employee e")
    long countAllEmployees();

    @Query("SELECT e.department.name, COUNT(e) FROM Employee e GROUP BY e.department.name")
    List<Object[]> countByDepartment();

    @Query("SELECT e.jobRole.title, COUNT(e) FROM Employee e GROUP BY e.jobRole.title")
    List<Object[]> countByJobRole();
}
