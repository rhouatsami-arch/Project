import { Injectable } from '@angular/core';
import { DOCUMENT } from '@angular/common';
import { inject } from '@angular/core';

export type ToastType = 'success' | 'error' | 'info';

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly doc = inject(DOCUMENT);
  private container: HTMLElement | null = null;

  private ensureContainer(): HTMLElement {
    if (this.container && this.doc.body.contains(this.container)) return this.container;
    const el = this.doc.createElement('div');
    el.className = 'tw-toasts';
    this.doc.body.appendChild(el);
    this.container = el;
    return el;
  }

  show(message: string, type: ToastType = 'info', duration = 3000) {
    const root = this.ensureContainer();
    const toast = this.doc.createElement('div');
    toast.className = `tw-toast ${type}`;
    toast.textContent = message;
    root.appendChild(toast);
    // Force reflow for animation
    void toast.offsetWidth;
    toast.classList.add('visible');
    const timer = setTimeout(() => this.dismiss(toast), duration);
    toast.addEventListener('click', () => {
      clearTimeout(timer);
      this.dismiss(toast);
    });
  }

  success(msg: string, duration?: number) { this.show(msg, 'success', duration); }
  error(msg: string, duration?: number) { this.show(msg, 'error', duration); }
  info(msg: string, duration?: number) { this.show(msg, 'info', duration); }

  private dismiss(toast: HTMLElement) {
    toast.classList.remove('visible');
    toast.addEventListener('transitionend', () => toast.remove(), { once: true });
  }
}
