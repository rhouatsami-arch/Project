import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TasksService, TaskDto } from '../../../core/services/tasks';
import { ToastService } from '../../../core/services/toast.service';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="tw-container" style="max-width: 1100px;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px;">
        <div>
          <h1 style="font-size: 32px; font-weight: 700; margin: 0 0 8px 0; background: var(--tw-gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            📋 Liste des tâches
          </h1>
          <p style="color: var(--tw-text-muted); margin: 0; font-size: 15px;">
            Gérez et suivez toutes vos tâches en un seul endroit
          </p>
        </div>
        <button class="btn" (click)="refresh()" style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 18px;">🔄</span>
          Rafraîchir
        </button>
      </div>

      <div *ngIf="loading" style="text-align: center; padding: 40px; color: var(--tw-text-muted);">
        <div style="font-size: 32px; margin-bottom: 12px;">⏳</div>
        <div>Chargement des tâches...</div>
      </div>

      <div class="card" *ngIf="!loading && tasks.length">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Titre</th>
                <th>P50 (min)</th>
                <th>P90 (min)</th>
                <th>Statut</th>
                <th style="text-align: right;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let t of tasks">
                <td>
                  <div style="font-weight: 600; color: var(--tw-text);">{{ t.title }}</div>
                  <div *ngIf="t.description" style="font-size: 13px; color: var(--tw-text-muted); margin-top: 2px;">{{ t.description }}</div>
                </td>
                <td>
                  <span style="font-weight: 600; color: var(--tw-primary-light);">{{ t.p50Minutes ?? t.predictedMinutes }}</span>
                </td>
                <td>
                  <span style="font-weight: 600; color: var(--tw-accent-light);">{{ t.p90Minutes ?? '-' }}</span>
                </td>
                <td>
                  <span class="status-badge" [class.status-completed]="t.status === 'COMPLETED'" [class.status-pending]="t.status === 'PENDING'" [class.status-in-progress]="t.status === 'IN_PROGRESS'">
                    {{ getStatusLabel(t.status) }}
                  </span>
                </td>
                <td style="text-align: right;">
                  <button class="btn-small btn-success" *ngIf="t.status !== 'COMPLETED'" (click)="openComplete(t)">
                    ✓ Compléter
                  </button>
                  <span *ngIf="t.status === 'COMPLETED'" style="color: var(--tw-success); font-size: 20px;">✅</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div *ngIf="!loading && tasks.length === 0" class="card" style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 64px; margin-bottom: 16px; opacity: 0.5;">📭</div>
        <div style="font-size: 18px; font-weight: 600; color: var(--tw-text); margin-bottom: 8px;">Aucune tâche</div>
        <div style="color: var(--tw-text-muted);">Commencez par créer votre première tâche</div>
      </div>

      <!-- Modal completion -->
      <div *ngIf="modalOpen" class="tw-modal-backdrop" (click)="cancelComplete()">
        <div class="tw-modal" (click)="$event.stopPropagation()">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 22px; font-weight: 700; color: var(--tw-text);">✅ Compléter la tâche</h3>
            <button class="btn-close" (click)="cancelComplete()">✕</button>
          </div>
          
          <div style="padding: 16px; background: rgba(139, 92, 246, 0.05); border-radius: 12px; border: 1px solid var(--tw-border); margin-bottom: 20px;">
            <div style="font-size: 14px; color: var(--tw-text-muted); margin-bottom: 4px;">Tâche</div>
            <div style="font-weight: 600; color: var(--tw-text);">{{ modalTask?.title }}</div>
          </div>

          <div class="field">
            <label for="actual">⏱️ Durée réelle (minutes)</label>
            <input id="actual" type="number" class="input" [(ngModel)]="modalActual" placeholder="Entrez la durée réelle" />
          </div>

          <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px;">
            <button class="btn-secondary" (click)="cancelComplete()">Annuler</button>
            <button class="btn" (click)="confirmComplete()">Valider</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: `
    .table-container {
      overflow-x: auto;
    }

    .status-badge {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .status-completed {
      background: rgba(16, 185, 129, 0.15);
      color: var(--tw-success);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-pending {
      background: rgba(251, 191, 36, 0.15);
      color: var(--tw-warning);
      border: 1px solid rgba(251, 191, 36, 0.3);
    }

    .status-in-progress {
      background: rgba(59, 130, 246, 0.15);
      color: var(--tw-info);
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .btn-small {
      padding: 8px 16px;
      border-radius: 8px;
      border: none;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .btn-success {
      background: var(--tw-gradient-success);
      color: white;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .btn-success:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }

    .btn-secondary {
      padding: 14px 28px;
      border-radius: 12px;
      border: 1px solid var(--tw-border);
      background: transparent;
      color: var(--tw-text);
      font-weight: 600;
      font-size: 15px;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .btn-secondary:hover {
      background: rgba(139, 92, 246, 0.05);
      border-color: var(--tw-border-bright);
    }

    .btn-close {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      border: 1px solid var(--tw-border);
      background: transparent;
      color: var(--tw-text-muted);
      font-size: 20px;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .btn-close:hover {
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.3);
      color: var(--tw-danger);
    }

    .tw-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      animation: fadeIn 0.3s ease;
    }

    .tw-modal {
      width: 500px;
      max-width: calc(100% - 32px);
      background: rgba(20, 25, 45, 0.95);
      backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid var(--tw-border-bright);
      border-radius: 20px;
      padding: 28px;
      box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `,
})
export class TaskList {
  tasks: TaskDto[] = [];
  loading = false;
  modalOpen = false;
  modalTask: TaskDto | null = null;
  modalActual: number | null = null;

  constructor(private tasksService: TasksService, private toasts: ToastService) {
    this.refresh();
  }

  refresh() {
    this.loading = true;
    this.tasksService.listTasks().subscribe({
      next: (items) => {
        this.tasks = items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  openComplete(t: TaskDto) {
    this.modalTask = t;
    this.modalActual = t.actualMinutes ?? null;
    this.modalOpen = true;
  }

  cancelComplete() {
    this.modalOpen = false;
    this.modalTask = null;
    this.modalActual = null;
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'PENDING': '⏳ En attente',
      'IN_PROGRESS': '🔄 En cours',
      'COMPLETED': '✅ Terminé'
    };
    return labels[status] || status;
  }

  confirmComplete() {
    const t = this.modalTask;
    const actual = Number(this.modalActual);
    if (!t) return;
    if (!Number.isFinite(actual) || actual <= 0) {
      this.toasts.error('Valeur invalide');
      return;
    }
    this.loading = true;
    this.tasksService.completeTask(t.id, actual).subscribe({
      next: () => {
        this.toasts.success('Tâche complétée');
        this.cancelComplete();
        this.refresh();
      },
      error: () => {
        this.loading = false;
        this.toasts.error('Erreur lors de la complétion');
      }
    });
  }
}
