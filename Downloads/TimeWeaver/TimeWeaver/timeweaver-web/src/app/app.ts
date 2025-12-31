import { Component, signal, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ThemeService } from './core/services/theme.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('timeweaver-web');

  constructor(private readonly theme: ThemeService) {
    this.theme.init();
  }

  get isDarkTheme(): boolean {
    return this.theme.currentTheme() === 'dark';
  }

  protected toggleTheme(): void {
    this.theme.toggle();
  }

  protected themeLabel() {
    return this.theme.currentTheme() === 'dark' ? 'Sombre' : 'Clair';
  }
}
