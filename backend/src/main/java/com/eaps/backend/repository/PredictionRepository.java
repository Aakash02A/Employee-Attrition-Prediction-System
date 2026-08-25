package com.eaps.backend.repository;

import com.eaps.backend.model.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PredictionRepository extends JpaRepository<Prediction, Long> {

    List<Prediction> findByEmployeeIdOrderByCreatedAtDesc(Long employeeId);

    List<Prediction> findAllByOrderByCreatedAtDesc();

    List<Prediction> findByRiskLevel(String riskLevel);

    /**
     * Returns the most recent prediction for a given employee (used to show
     * "current" risk status on the employee list).
     */
    Optional<Prediction> findFirstByEmployeeIdOrderByCreatedAtDesc(Long employeeId);

    // --- Analytics queries ---

    @Query("SELECT COUNT(p) FROM Prediction p WHERE p.prediction = 'LEAVE'")
    long countAttrition();

    @Query("SELECT AVG(p.probability) FROM Prediction p")
    Double averageProbability();

    @Query("SELECT COUNT(p) FROM Prediction p WHERE p.riskLevel = 'HIGH'")
    long countHighRisk();

    /**
     * Attrition count grouped by department — joins through employee.
     */
    @Query("SELECT e.department.name, COUNT(p) FROM Prediction p " +
           "JOIN p.employee e WHERE p.prediction = 'LEAVE' " +
           "GROUP BY e.department.name")
    List<Object[]> countAttritionByDepartment();

    /**
     * Attrition count grouped by job role.
     */
    @Query("SELECT e.jobRole.title, COUNT(p) FROM Prediction p " +
           "JOIN p.employee e WHERE p.prediction = 'LEAVE' " +
           "GROUP BY e.jobRole.title")
    List<Object[]> countAttritionByJobRole();

    /**
     * Attrition count grouped by age bracket.
     */
    @Query("SELECT CASE " +
           "  WHEN e.age BETWEEN 18 AND 25 THEN '18-25' " +
           "  WHEN e.age BETWEEN 26 AND 35 THEN '26-35' " +
           "  WHEN e.age BETWEEN 36 AND 45 THEN '36-45' " +
           "  WHEN e.age BETWEEN 46 AND 55 THEN '46-55' " +
           "  ELSE '55+' END, COUNT(p) " +
           "FROM Prediction p JOIN p.employee e " +
           "WHERE p.prediction = 'LEAVE' " +
           "GROUP BY CASE " +
           "  WHEN e.age BETWEEN 18 AND 25 THEN '18-25' " +
           "  WHEN e.age BETWEEN 26 AND 35 THEN '26-35' " +
           "  WHEN e.age BETWEEN 36 AND 45 THEN '36-45' " +
           "  WHEN e.age BETWEEN 46 AND 55 THEN '46-55' " +
           "  ELSE '55+' END")
    List<Object[]> countAttritionByAgeGroup();

    /**
     * Attrition count grouped by salary range.
     */
    @Query("SELECT CASE " +
           "  WHEN e.monthlyIncome < 2500 THEN 'Below $2.5k' " +
           "  WHEN e.monthlyIncome BETWEEN 2500 AND 5000 THEN '$2.5k-$5k' " +
           "  WHEN e.monthlyIncome BETWEEN 5001 AND 10000 THEN '$5k-$10k' " +
           "  ELSE '$10k+' END, COUNT(p) " +
           "FROM Prediction p JOIN p.employee e " +
           "WHERE p.prediction = 'LEAVE' " +
           "GROUP BY CASE " +
           "  WHEN e.monthlyIncome < 2500 THEN 'Below $2.5k' " +
           "  WHEN e.monthlyIncome BETWEEN 2500 AND 5000 THEN '$2.5k-$5k' " +
           "  WHEN e.monthlyIncome BETWEEN 5001 AND 10000 THEN '$5k-$10k' " +
           "  ELSE '$10k+' END")
    List<Object[]> countAttritionBySalaryRange();

    /**
     * Attrition count grouped by overtime status.
     */
    @Query("SELECT e.overTime, COUNT(p) FROM Prediction p " +
           "JOIN p.employee e WHERE p.prediction = 'LEAVE' " +
           "GROUP BY e.overTime")
    List<Object[]> countAttritionByOvertime();

    /**
     * Attrition count grouped by job satisfaction level.
     */
    @Query("SELECT e.jobSatisfaction, COUNT(p) FROM Prediction p " +
           "JOIN p.employee e WHERE p.prediction = 'LEAVE' " +
           "GROUP BY e.jobSatisfaction ORDER BY e.jobSatisfaction")
    List<Object[]> countAttritionByJobSatisfaction();

    /**
     * Attrition count grouped by years-at-company bracket.
     */
    @Query("SELECT CASE " +
           "  WHEN e.yearsAtCompany BETWEEN 0 AND 2 THEN '0-2 Years' " +
           "  WHEN e.yearsAtCompany BETWEEN 3 AND 5 THEN '3-5 Years' " +
           "  WHEN e.yearsAtCompany BETWEEN 6 AND 10 THEN '6-10 Years' " +
           "  ELSE '11+ Years' END, COUNT(p) " +
           "FROM Prediction p JOIN p.employee e " +
           "WHERE p.prediction = 'LEAVE' " +
           "GROUP BY CASE " +
           "  WHEN e.yearsAtCompany BETWEEN 0 AND 2 THEN '0-2 Years' " +
           "  WHEN e.yearsAtCompany BETWEEN 3 AND 5 THEN '3-5 Years' " +
           "  WHEN e.yearsAtCompany BETWEEN 6 AND 10 THEN '6-10 Years' " +
           "  ELSE '11+ Years' END")
    List<Object[]> countAttritionByYearsAtCompany();

    /**
     * High-risk employees — latest prediction per employee where risk = HIGH.
     * Returns employee IDs and their probabilities for the high-risk list page.
     */
    @Query("SELECT p FROM Prediction p WHERE p.id IN (" +
           "  SELECT MAX(p2.id) FROM Prediction p2 GROUP BY p2.employee.id" +
           ") AND p.riskLevel = :riskLevel ORDER BY p.probability DESC")
    List<Prediction> findLatestPredictionsByRiskLevel(@Param("riskLevel") String riskLevel);
}
