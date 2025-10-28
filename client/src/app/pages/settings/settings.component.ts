import { Component, inject } from '@angular/core';
import { NzCheckboxModule } from 'ng-zorro-antd/checkbox';
import { NzSwitchModule } from 'ng-zorro-antd/switch';
import { FormsModule } from '@angular/forms';
import { Theme, ThemeService } from '../../theme.service';

@Component({
  selector: 'app-settings',
  imports: [
    NzCheckboxModule,
    NzSwitchModule,
    FormsModule
  ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
})
export class SettingsComponent {
  readonly themeService:ThemeService = inject(ThemeService);
  readonly themes = this.themeService.themes;

  get currentTheme(): Theme {
    return this.themeService.theme();
  }

  checked = this.currentTheme=='light';

  onSelect = (theme: Theme) => this.themeService.applyTheme(theme);

  themeSwitch() {
    this.onSelect(this.checked ? 'dark' : 'light');
  }
}
