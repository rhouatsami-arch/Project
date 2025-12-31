package com.timeweaver.timetracking.config;

import com.timeweaver.timetracking.model.Task;
import com.timeweaver.timetracking.repo.TaskRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import java.time.Instant;

@Configuration
@Profile("dev")
public class DevDataLoader {

    @Bean
    CommandLineRunner seedTasks(TaskRepository tasks) {
        return args -> {
            if (tasks.count() == 0) {
                // Tâche 1 - en cours, complexité MEDIUM
                Task t1 = new Task();
                t1.setUserId(1L);
                t1.setTitle("Tâche d'exemple");
                t1.setDescription("Première tâche créée automatiquement en profil dev");
                t1.setComplexity("MEDIUM");
                t1.setPredictedMinutes(45);
                t1.setP50Minutes(45);
                t1.setP90Minutes(75);
                t1.setStatus("IN_PROGRESS");
                t1.setCreatedAt(Instant.now());
                tasks.save(t1);

                // Tâche 2 - en cours, complexité LOW
                Task t2 = new Task();
                t2.setUserId(1L);
                t2.setTitle("Configurer l'environnement dev");
                t2.setDescription("Installer les outils et vérifier les services");
                t2.setComplexity("LOW");
                t2.setPredictedMinutes(20);
                t2.setP50Minutes(20);
                t2.setP90Minutes(35);
                t2.setStatus("IN_PROGRESS");
                t2.setCreatedAt(Instant.now());
                tasks.save(t2);

                // Tâche 3 - complétée, complexité HIGH
                Task t3 = new Task();
                t3.setUserId(2L);
                t3.setTitle("Intégrer l'API Gateway");
                t3.setDescription("Routage via Eureka et filtre de corrélation");
                t3.setComplexity("HIGH");
                t3.setPredictedMinutes(60);
                t3.setP50Minutes(60);
                t3.setP90Minutes(90);
                t3.setActualMinutes(55);
                t3.setStatus("COMPLETED");
                t3.setCreatedAt(Instant.now());
                t3.setCompletedAt(Instant.now());
                tasks.save(t3);
            }
        };
    }
}
