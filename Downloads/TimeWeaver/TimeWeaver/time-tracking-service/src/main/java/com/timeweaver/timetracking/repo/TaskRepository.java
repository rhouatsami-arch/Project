package com.timeweaver.timetracking.repo;

import com.timeweaver.timetracking.model.Task;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaskRepository extends JpaRepository<Task, Long> {
}
