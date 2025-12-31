import { Injectable, signal } from '@angular/core';
import { DOCUMENT } from '@angular/common';
import { inject } from '@angular/core';

export type Theme = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'tw-theme';
  private readonly doc: Document = inject(DOCUMENT);

  readonly currentTheme = signal<Theme>('light');

  init(): void {
    const stored = (localStorage.getItem(this.storageKey) as Theme | null);
    const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme: Theme = stored ?? (systemPrefersDark ? 'dark' : 'light');
    this.applyTheme(theme);
  }

  toggle(): void {
    const next: Theme = this.currentTheme() === 'dark' ? 'light' : 'dark';
    this.applyTheme(next);
  }

  private applyTheme(theme: Theme): void {
    this.currentTheme.set(theme);
    this.doc.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);
  }
}
