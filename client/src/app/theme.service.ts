import { Injectable, Renderer2, RendererFactory2, signal } from '@angular/core';

export type Theme = 'light' | 'dark' | 'system';
const LOCAL_STORAGE_COLOR_SCHEME = 'color-scheme';


@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  readonly #renderer: Renderer2;
  readonly #themeSignal = signal(this.#getInitialTheme());

  constructor(rendererFactory: RendererFactory2) {
    this.#renderer = rendererFactory.createRenderer(null, null);
    this.applyTheme(this.#themeSignal());
  }

  get theme() {
    return this.#themeSignal.asReadonly();
  }

  get themes() {
    return [
      { value: 'dark', label: 'Dark' },
      { value: 'light', label: 'Light' },
      { value: 'system', label: 'System' },
    ] as const;
  }

  #getInitialTheme(): Theme {
    const storedTheme = localStorage.getItem(LOCAL_STORAGE_COLOR_SCHEME);
    const themeExists = this.themes.some(({ value }) => value === storedTheme);

    return themeExists ? (storedTheme as Theme) : 'system';
  }

  /**
   * Applies the selected theme and updates local storage.
   * If the theme is set to 'system', it automatically adjusts to 'light' or 'dark'
   * based on the user's system preference.
   *
   * @param theme - The theme to apply: 'light', 'dark', or 'system'.
   */
  applyTheme(theme: Theme) {
    const scheme = theme === 'system' ? 'light dark' : theme;

    this.#renderer.setStyle(document.documentElement, 'color-scheme', scheme);
    this.#themeSignal.set(theme);

    localStorage.setItem(LOCAL_STORAGE_COLOR_SCHEME, theme);
  }
}
