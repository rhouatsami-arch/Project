package com.timeweaver.aiprediction.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Objects;

@RestController
@RequestMapping("/api/predict")
public class AiPredictionController {

    @PostMapping
    public ResponseEntity<PredictionResponse> predict(@RequestBody PredictionRequest request) {
        // Baseline heuristique simple
        int base = 30; // minutes
        int complexity = switch (Objects.toString(request.getComplexity(), "MEDIUM").toUpperCase()) {
            case "LOW" -> 0;
            case "HIGH" -> 30;
            default -> 15;
        };
        int descFactor = request.getDescription() == null ? 0 : Math.min(30, request.getDescription().length() / 20);
        int prior = request.getHistoricalAvgMinutes() != null ? (int) Math.round(request.getHistoricalAvgMinutes() * 0.5) : 0;
        int mostLikely = Math.max(5, base + complexity + descFactor + prior);

        // Convertir en intervalle via une approximation PERT (optimistic, most likely, pessimistic)
        double optimistic = Math.max(1, Math.round(mostLikely * 0.7));
        double pessimistic = Math.max(optimistic + 1, Math.round(mostLikely * 1.8));

        // P50 ~ moyenne PERT
        double mean = (optimistic + 4 * mostLikely + pessimistic) / 6.0;
        // Ecart-type approx PERT
        double std = (pessimistic - optimistic) / 6.0;
        // Approx P90 ~ mean + 1.2816 * std, bornée à pessimistic
        double p90 = Math.min(pessimistic, Math.ceil(mean + 1.2816 * std));
        int p50 = (int) Math.round(mean);

        PredictionResponse res = new PredictionResponse(p50, (int) Math.round(p90));
        return ResponseEntity.ok(res);
    }

    public static class PredictionRequest {
        private String title;
        private String description;
        private String complexity; // LOW, MEDIUM, HIGH
        private Integer historicalAvgMinutes;

        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public String getComplexity() { return complexity; }
        public void setComplexity(String complexity) { this.complexity = complexity; }
        public Integer getHistoricalAvgMinutes() { return historicalAvgMinutes; }
        public void setHistoricalAvgMinutes(Integer historicalAvgMinutes) { this.historicalAvgMinutes = historicalAvgMinutes; }
    }

    public static class PredictionResponse {
        private int p50Minutes;
        private int p90Minutes;
        public PredictionResponse() {}
        public PredictionResponse(int p50Minutes, int p90Minutes) {
            this.p50Minutes = p50Minutes;
            this.p90Minutes = p90Minutes;
        }
        public int getP50Minutes() { return p50Minutes; }
        public void setP50Minutes(int p50Minutes) { this.p50Minutes = p50Minutes; }
        public int getP90Minutes() { return p90Minutes; }
        public void setP90Minutes(int p90Minutes) { this.p90Minutes = p90Minutes; }
    }
}
