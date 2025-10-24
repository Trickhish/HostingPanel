import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faHouse, faGlobe, faDatabase, faUsers, faGear } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-layout',
  imports: [CommonModule, RouterModule, RouterOutlet, FontAwesomeModule],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent {
  pageTitle = "Layout";
}