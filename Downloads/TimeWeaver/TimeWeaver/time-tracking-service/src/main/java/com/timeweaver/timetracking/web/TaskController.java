package com.timeweaver.timetracking.web;

import com.timeweaver.timetracking.client.AiPredictionClient;
import com.timeweaver.timetracking.config.RabbitConfig;
import com.timeweaver.timetracking.model.Task;
import com.timeweaver.timetracking.repo.TaskRepository;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.List;

@RestController
@CrossOrigin(origins = "http://localhost:4200")
@RequestMapping("/api/tasks")
@SuppressWarnings("null")
public class TaskController {

    private final TaskRepository taskRepository;
    private final AiPredictionClient aiClient;
    private final RabbitTemplate rabbitTemplate;

    public TaskController(TaskRepository taskRepository, AiPredictionClient aiClient, RabbitTemplate rabbitTemplate) {
        this.taskRepository = taskRepository;
        this.aiClient = aiClient;
        this.rabbitTemplate = rabbitTemplate;
    }

    @PostMapping
    public ResponseEntity<Task> create(@RequestBody CreateTaskRequest req) {
        int p50 = 0;
        int p90 = 0;

        try {
            AiPredictionClient.PredictionRequest preq = new AiPredictionClient.PredictionRequest();
            preq.setTitle(req.title);
            preq.setDescription(req.description);
            preq.setComplexity(req.complexity);
            preq.setHistoricalAvgMinutes(req.historicalAvgMinutes);

            AiPredictionClient.PredictionResponse pres = aiClient.predict(preq);
            if (pres != null) {
                p50 = pres.getP50Minutes();
                p90 = pres.getP90Minutes();
            }
        } catch (Exception e) {
            // Fallback if AI service is down
            System.err.println("AI Prediction service unavailable, using defaults: " + e.getMessage());
        }

        Task t = new Task();
        t.setUserId(req.userId);
        t.setTitle(req.title);
        t.setDescription(req.description);
        t.setComplexity(req.complexity);
        // Compat: predictedMinutes = P50
        t.setPredictedMinutes(p50);
        t.setP50Minutes(p50);
        t.setP90Minutes(p90);
        t.setStatus("IN_PROGRESS");
        t.setCreatedAt(Instant.now());

        Task saved = taskRepository.save(t);
        if (saved.getId() == null)
            throw new IllegalStateException("Saved task has no ID");

        return ResponseEntity.created(URI.create("/api/tasks/" + saved.getId())).body(saved);
    }

    @GetMapping
    public ResponseEntity<List<Task>> list() {
        return ResponseEntity.ok(taskRepository.findAll());
    }

    @PostMapping("/{id}/complete")
    public ResponseEntity<Task> complete(@PathVariable("id") Long id, @RequestBody CompleteTaskRequest req) {
        Optional<Task> opt = taskRepository.findById(id);
        if (opt.isEmpty())
            return ResponseEntity.notFound().build();
        Task t = opt.get();
        t.setActualMinutes(req.actualMinutes);
        t.setCompletedAt(Instant.now());
        t.setStatus("COMPLETED");
        Task saved = taskRepository.save(t);

        Integer predicted = saved.getPredictedMinutes();
        Integer actual = saved.getActualMinutes();
        if (predicted != null && actual != null) {
            int delta = actual - predicted; // positive = loss, negative = gain
            String outcome = delta <= 0 ? "GAIN" : "LOSS";
            Map<String, Object> payload = Map.of(
                    "taskId", saved.getId(),
                    "userId", saved.getUserId(),
                    "predictedMinutes", predicted,
                    "actualMinutes", actual,
                    "delta", delta,
                    "outcome", outcome);
            rabbitTemplate.convertAndSend(RabbitConfig.NOTIFICATIONS_QUEUE, payload);
        }

        return ResponseEntity.ok(saved);
    }

    public static class CreateTaskRequest {
        public Long userId;
        public String title;
        public String description;
        public String complexity;
        public Integer historicalAvgMinutes;
    }

    public static class CompleteTaskRequest {
        public Integer actualMinutes;
    }
}
