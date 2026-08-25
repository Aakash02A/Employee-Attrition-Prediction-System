package com.eaps.backend.controller;

import com.eaps.backend.dto.AnalyticsResponse;
import com.eaps.backend.dto.DashboardKpiResponse;
import com.eaps.backend.service.AnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    @GetMapping("/dashboard")
    public ResponseEntity<DashboardKpiResponse> getDashboardKpis() {
        return ResponseEntity.ok(analyticsService.getDashboardKpis());
    }

    @GetMapping("/by-department")
    public ResponseEntity<AnalyticsResponse> getByDepartment() {
        return ResponseEntity.ok(analyticsService.getAttritionByDepartment());
    }

    @GetMapping("/by-role")
    public ResponseEntity<AnalyticsResponse> getByRole() {
        return ResponseEntity.ok(analyticsService.getAttritionByJobRole());
    }

    @GetMapping("/by-age")
    public ResponseEntity<AnalyticsResponse> getByAge() {
        return ResponseEntity.ok(analyticsService.getAttritionByAgeGroup());
    }

    @GetMapping("/by-salary")
    public ResponseEntity<AnalyticsResponse> getBySalary() {
        return ResponseEntity.ok(analyticsService.getAttritionBySalaryRange());
    }

    @GetMapping("/by-overtime")
    public ResponseEntity<AnalyticsResponse> getByOvertime() {
        return ResponseEntity.ok(analyticsService.getAttritionByOvertime());
    }

    @GetMapping("/by-satisfaction")
    public ResponseEntity<AnalyticsResponse> getBySatisfaction() {
        return ResponseEntity.ok(analyticsService.getAttritionByJobSatisfaction());
    }

    @GetMapping("/by-years")
    public ResponseEntity<AnalyticsResponse> getByYearsAtCompany() {
        return ResponseEntity.ok(analyticsService.getAttritionByYearsAtCompany());
    }
}
