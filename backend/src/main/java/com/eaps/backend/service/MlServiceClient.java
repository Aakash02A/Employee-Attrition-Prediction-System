package com.eaps.backend.service;

import org.springframework.web.client.RestTemplate;
import com.eaps.backend.dto.MlServiceRequest;
import com.eaps.backend.dto.MlServiceResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

/**
 * HTTP client for communicating with the FastAPI ML microservice.
 * Uses Spring 6's {@link RestClient} (the modern replacement for RestTemplate).
 */
@Service
@Slf4j
public class MlServiceClient {


    private final RestTemplate restTemplate;

    public MlServiceClient(@Value("${ml.service.url}") String mlServiceUrl) {
        this.restTemplate = new RestTemplate();
        // Since we removed baseUrl from restTemplate setup, we will need to store the baseUrl
        // But for now let's just create a field for it
    }
    
    @Value("${ml.service.url}") 
    private String baseUrl;

    /**
     * Calls {@code POST /predict} on the FastAPI service.
     *
     * @param request employee features matching the Pydantic schema
     * @return prediction result from the ML model
     * @throws RestClientException if the ML service is unreachable or returns an error
     */
    public MlServiceResponse predict(MlServiceRequest request) {
        log.info("Calling ML service POST /predict");
        try {
            MlServiceResponse response = restTemplate.postForObject(baseUrl + "/predict", request, MlServiceResponse.class);
            if (response != null) {
                log.info("ML service returned: prediction={}, probability={}, risk={}",
                        response.getPrediction(), response.getProbability(), response.getRiskLevel());
            }
            return response;
        } catch (Exception e) {
            log.error("Failed to call ML service: {}", e.getMessage());
            throw new RuntimeException("ML service is unavailable. Please ensure it is running on the configured URL.", e);
        }
    }

    /**
     * Calls {@code GET /health} on the FastAPI service.
     *
     * @return true if the ML service is healthy
     */
    public boolean isHealthy() {
        try {
            restTemplate.getForObject(baseUrl + "/health", String.class);
            return true;
        } catch (Exception e) {
            log.warn("ML service health check failed: {}", e.getMessage());
            return false;
        }
    }
}
