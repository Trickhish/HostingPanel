import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateService, TranslateModule } from '@ngx-translate/core';
import { Theme, ThemeService } from './theme.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TranslateModule],
  //templateUrl: './app.component.html',
  template: `
    <router-outlet></router-outlet>
  `,
  styleUrl: './app.component.scss'
})
export class AppComponent {
  constructor(private translate: TranslateService) {
    translate.addLangs(['en', 'fr']);
    translate.setDefaultLang('en');

    // First check localStorage for saved preference
    const savedLang = localStorage.getItem('preferredLanguage');

    if (savedLang && ['en', 'fr'].includes(savedLang)) {
      // Use saved language preference
      translate.use(savedLang);
    } else {
      // Fallback to browser language or default
      const browserLang = translate.getBrowserLang();
      const langToUse = browserLang?.match(/en|fr/) ? browserLang : 'en';
      translate.use(langToUse);
      // Save the initial language choice
      localStorage.setItem('preferredLanguage', langToUse);
    }
  }

  switchLanguage(lang: string) {
    this.translate.use(lang);
  }

  readonly themeService:ThemeService = inject(ThemeService);
  readonly themes = this.themeService.themes;

  get currentTheme(): Theme {
    return this.themeService.theme();
  }

  onSelect = (theme: Theme) => this.themeService.applyTheme(theme);
  
  title = 'hosting-panel';
}
