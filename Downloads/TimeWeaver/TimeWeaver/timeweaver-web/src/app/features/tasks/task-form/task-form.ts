import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { TasksService, CreateTaskRequest, TaskDto } from '../../../core/services/tasks';
import { ToastService } from '../../../core/services/toast.service';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="tw-container" style="max-width: 720px;">
      <div style="margin-bottom: 32px;">
        <h1 style="font-size: 32px; font-weight: 700; margin: 0 0 8px 0; background: var(--tw-gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
          ✨ Nouvelle tâche
        </h1>
        <p style="color: var(--tw-text-muted); margin: 0; font-size: 15px;">
          Créez une nouvelle tâche et obtenez une estimation intelligente du temps nécessaire
        </p>
      </div>

      <div class="card">
        <form [formGroup]="form" (ngSubmit)="onSubmit()" novalidate>
          <div class="field">
            <label for="userId">👤 Utilisateur</label>
            <input id="userId" type="number" class="input" formControlName="userId" placeholder="ID de l'utilisateur" />
            <small *ngIf="form.get('userId')?.touched && form.get('userId')?.invalid" style="color: var(--tw-warning); font-size: 13px;">⚠️ Champ requis</small>
          </div>

          <div class="field">
            <label for="title">📝 Titre</label>
            <input id="title" type="text" class="input" formControlName="title" placeholder="Ex: Développer la page d'accueil" />
            <small *ngIf="form.get('title')?.touched && form.get('title')?.invalid" style="color: var(--tw-warning); font-size: 13px;">⚠️ Champ requis</small>
          </div>

          <div class="field">
            <label for="description">📄 Description</label>
            <textarea id="description" rows="4" class="input" formControlName="description" placeholder="Décrivez les détails de la tâche..."></textarea>
          </div>

          <div class="field">
            <label for="complexity">⚡ Complexité</label>
            <select id="complexity" class="input" formControlName="complexity">
              <option value="LOW">🟢 Faible</option>
              <option value="MEDIUM">🟡 Moyenne</option>
              <option value="HIGH">🔴 Élevée</option>
            </select>
            <small *ngIf="form.get('complexity')?.touched && form.get('complexity')?.invalid" style="color: var(--tw-warning); font-size: 13px;">⚠️ Champ requis</small>
          </div>

          <div class="field">
            <label for="historicalAvgMinutes">⏱️ Moyenne historique (minutes)</label>
            <input id="historicalAvgMinutes" type="number" class="input" formControlName="historicalAvgMinutes" placeholder="Optionnel" />
          </div>

          <button class="btn" type="submit" [disabled]="form.invalid || loading" style="width: 100%; margin-top: 8px;">
            {{ loading ? '⏳ Création en cours…' : '🚀 Créer et estimer' }}
          </button>
        </form>
      </div>

      <div *ngIf="result" class="card" style="margin-top: 24px; border: 1px solid var(--tw-border-bright); background: rgba(139, 92, 246, 0.05); animation: slideIn 0.4s ease;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; border-radius: 12px; background: var(--tw-gradient-primary); display: flex; align-items: center; justify-content: center; font-size: 24px;">
            ✅
          </div>
          <div>
            <div style="font-weight: 700; font-size: 18px; color: var(--tw-text);">Tâche créée avec succès!</div>
            <div style="color: var(--tw-text-muted); font-size: 14px;">Voici l'estimation de temps</div>
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-top: 20px;">
          <div style="padding: 16px; background: rgba(139, 92, 246, 0.1); border-radius: 12px; border: 1px solid var(--tw-border);">
            <div style="color: var(--tw-text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">P50 (Médiane)</div>
            <div style="font-size: 24px; font-weight: 700; color: var(--tw-primary-light);">{{ result.p50Minutes }} <span style="font-size: 14px; font-weight: 500;">min</span></div>
          </div>
          
          <div style="padding: 16px; background: rgba(6, 182, 212, 0.1); border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.2);">
            <div style="color: var(--tw-text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">P90 (Pessimiste)</div>
            <div style="font-size: 24px; font-weight: 700; color: var(--tw-accent-light);">{{ result.p90Minutes }} <span style="font-size: 14px; font-weight: 500;">min</span></div>
          </div>
          
          <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2);">
            <div style="color: var(--tw-text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Statut</div>
            <div style="font-size: 18px; font-weight: 600; color: var(--tw-success);">{{ result.status }}</div>
          </div>
        </div>
      </div>
    </div>

    <style>
      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    </style>
  `,
  styles: ``,
})
export class TaskForm {
  loading = false;
  result: TaskDto | null = null;

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private tasks: TasksService,
    private toast: ToastService
  ) {
    this.form = this.fb.group({
      userId: this.fb.control<number | null>(1, { validators: [Validators.required] }),
      title: this.fb.control<string>('', { validators: [Validators.required] }),
      description: this.fb.control<string>(''),
      complexity: this.fb.control<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM', { validators: [Validators.required] }),
      historicalAvgMinutes: this.fb.control<number | null>(null)
    });
  }

  onSubmit() {
    if (this.form.invalid) return;
    const payload = this.form.value as unknown as CreateTaskRequest;
    this.loading = true;
    this.result = null;
    this.tasks.createTask(payload).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
        this.toast.success('✨ Tâche créée et enregistrée avec succès !');
        this.form.reset({
          userId: 1,
          complexity: 'MEDIUM'
        });
      },
      error: (err) => {
        this.loading = false;
        console.error('Erreur lors de la création de la tâche:', err);
        this.toast.error('❌ Erreur lors de l\'enregistrement de la tâche. Vérifiez que les services backend sont démarrés.');
      }
    });
  }
}
