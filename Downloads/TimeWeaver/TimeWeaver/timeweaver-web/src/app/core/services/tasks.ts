import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CreateTaskRequest {
  userId: number;
  title: string;
  description?: string;
  complexity: 'LOW' | 'MEDIUM' | 'HIGH';
  historicalAvgMinutes?: number;
}

export interface TaskDto {
  id: number;
  userId: number;
  title: string;
  description?: string;
  complexity: 'LOW' | 'MEDIUM' | 'HIGH';
  predictedMinutes?: number;
  p50Minutes?: number;
  p90Minutes?: number;
  actualMinutes?: number;
  status: string;
  createdAt?: string;
  completedAt?: string;
}

@Injectable({
  providedIn: 'root'
})
export class TasksService {
  constructor(private http: HttpClient) {}

  createTask(payload: CreateTaskRequest): Observable<TaskDto> {
    return this.http.post<TaskDto>('/api/tasks', payload);
  }

  listTasks(): Observable<TaskDto[]> {
    return this.http.get<TaskDto[]>('/api/tasks');
  }

  completeTask(id: number, actualMinutes: number): Observable<TaskDto> {
    return this.http.post<TaskDto>(`/api/tasks/${id}/complete`, { actualMinutes });
  }
}
