package com.timeweaver.timetracking.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long userId;
    private String title;

    @Column(length = 2000)
    private String description;

    private String complexity; // LOW, MEDIUM, HIGH

    private Integer predictedMinutes;
    private Integer p50Minutes;
    private Integer p90Minutes;
    private Integer actualMinutes;

    private String status; // CREATED, IN_PROGRESS, COMPLETED

    private Instant createdAt;
    private Instant completedAt;

    @PrePersist
    public void prePersist() {
        this.createdAt = Instant.now();
        if (this.status == null) this.status = "CREATED";
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getComplexity() { return complexity; }
    public void setComplexity(String complexity) { this.complexity = complexity; }
    public Integer getPredictedMinutes() { return predictedMinutes; }
    public void setPredictedMinutes(Integer predictedMinutes) { this.predictedMinutes = predictedMinutes; }
    public Integer getP50Minutes() { return p50Minutes; }
    public void setP50Minutes(Integer p50Minutes) { this.p50Minutes = p50Minutes; }
    public Integer getP90Minutes() { return p90Minutes; }
    public void setP90Minutes(Integer p90Minutes) { this.p90Minutes = p90Minutes; }
    public Integer getActualMinutes() { return actualMinutes; }
    public void setActualMinutes(Integer actualMinutes) { this.actualMinutes = actualMinutes; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getCompletedAt() { return completedAt; }
    public void setCompletedAt(Instant completedAt) { this.completedAt = completedAt; }
}
