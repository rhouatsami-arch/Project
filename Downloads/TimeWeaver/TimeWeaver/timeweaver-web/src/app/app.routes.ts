import { Routes } from '@angular/router';
import { TaskForm } from './features/tasks/task-form/task-form';
import { TaskList } from './features/tasks/task-list/task-list';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'tasks/new' },
  { path: 'tasks/new', component: TaskForm },
  { path: 'tasks', component: TaskList },
  { path: '**', redirectTo: 'tasks/new' }
];
