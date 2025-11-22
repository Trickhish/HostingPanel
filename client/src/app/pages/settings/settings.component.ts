import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzCheckboxModule } from 'ng-zorro-antd/checkbox';
import { NzSwitchModule } from 'ng-zorro-antd/switch';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Theme, ThemeService } from '../../theme.service';

@Component({
  selector: 'app-settings',
  imports: [
    CommonModule,
    NzCheckboxModule,
    NzSwitchModule,
    NzSelectModule,
    FormsModule,
    TranslateModule
  ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent {
  readonly themeService: ThemeService = inject(ThemeService);
  readonly translateService: TranslateService = inject(TranslateService);
  readonly themes = this.themeService.themes;

  // Available languages
  languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' }
  ];

  // Current language
  currentLanguage: string = this.translateService.currentLang || this.translateService.defaultLang || 'en';

  get currentTheme(): Theme {
    return this.themeService.theme();
  }

  checked = this.currentTheme == 'light';

  onSelect = (theme: Theme) => this.themeService.applyTheme(theme);

  themeSwitch() {
    this.onSelect(this.checked ? 'dark' : 'light');
  }

  changeLanguage(langCode: string) {
    this.translateService.use(langCode);
    this.currentLanguage = langCode;
    localStorage.setItem('preferredLanguage', langCode);
  }
}
