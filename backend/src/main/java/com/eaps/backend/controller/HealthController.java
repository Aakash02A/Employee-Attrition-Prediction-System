package com.eaps.backend.controller;

import com.eaps.backend.service.MlServiceClient;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class HealthController {

    private final MlServiceClient mlServiceClient;

    /**
     * Combined health check: backend status + ML service connectivity.
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        boolean mlHealthy = mlServiceClient.isHealthy();

        Map<String, Object> status = Map.of(
                "status", "ok",
                "service", "Employee Attrition Backend",
                "mlService", mlHealthy ? "connected" : "unavailable"
        );

        return ResponseEntity.ok(status);
    }
}
