package com.eaps.backend.controller;

import com.eaps.backend.dto.PredictionRequest;
import com.eaps.backend.dto.PredictionResponse;
import com.eaps.backend.service.PredictionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class PredictionController {

    private final PredictionService predictionService;

    /**
     * Run attrition prediction for an employee.
     * Calls the FastAPI ML service and persists the result.
     */
    @PostMapping("/predict")
    @PreAuthorize("hasAnyRole('ADMIN', 'HR')")
    public ResponseEntity<PredictionResponse> predict(@Valid @RequestBody PredictionRequest request) {
        // TODO Phase 8: extract username from JWT SecurityContext
        String requestedBy = "admin";
        PredictionResponse response = predictionService.predictAttrition(request.getEmployeeId(), requestedBy);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Get all prediction history, most recent first.
     */
    @GetMapping("/predictions")
    public ResponseEntity<List<PredictionResponse>> getAllPredictions() {
        return ResponseEntity.ok(predictionService.getAllPredictions());
    }

    /**
     * Get prediction history for a specific employee.
     */
    @GetMapping("/predictions/employee/{employeeId}")
    public ResponseEntity<List<PredictionResponse>> getPredictionsByEmployee(@PathVariable Long employeeId) {
        return ResponseEntity.ok(predictionService.getPredictionsByEmployee(employeeId));
    }

    /**
     * Get high-risk employees (latest prediction with risk_level = HIGH).
     */
    @GetMapping("/predictions/high-risk")
    public ResponseEntity<List<PredictionResponse>> getHighRiskEmployees() {
        return ResponseEntity.ok(predictionService.getHighRiskEmployees());
    }
}
