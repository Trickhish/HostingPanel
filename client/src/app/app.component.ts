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
    
    // Use browser language or default
    const browserLang = translate.getBrowserLang();
    translate.use(browserLang?.match(/en|fr|/) ? browserLang : 'fr');
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
