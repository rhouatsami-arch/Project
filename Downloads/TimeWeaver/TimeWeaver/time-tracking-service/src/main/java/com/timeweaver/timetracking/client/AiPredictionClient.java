package com.timeweaver.timetracking.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

@FeignClient(name = "ai-prediction-service")
public interface AiPredictionClient {

    @PostMapping("/api/predict")
    PredictionResponse predict(@RequestBody PredictionRequest request);

    class PredictionRequest {
        private String title;
        private String description;
        private String complexity;
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

    class PredictionResponse {
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
