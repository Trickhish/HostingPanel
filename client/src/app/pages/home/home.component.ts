import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../api.service';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

interface DashboardStats {
  totalWebsites: number;
  activeWebsites: number;
  totalBackups: number;
  diskUsage: number;
  diskQuota: number;
}

@Component({
  selector: 'app-home',
  imports: [CommonModule, RouterModule, TranslateModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  stats: DashboardStats = {
    totalWebsites: 0,
    activeWebsites: 0,
    totalBackups: 0,
    diskUsage: 0,
    diskQuota: 10000 // 10GB default
  };

  websites: any[] = [];
  recentActivity: any[] = [];
  isLoading = true;

  constructor(
    private apiService: ApiService,
    public authService: AuthService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.isLoading = true;

    // Load websites
    this.apiService.getWebsites().subscribe({
      next: (response) => {
        if (response.success) {
          this.websites = response.websites;
          this.calculateStats();
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading dashboard data:', error);
        this.isLoading = false;
      }
    });
  }

  calculateStats() {
    this.stats.totalWebsites = this.websites.length;
    this.stats.activeWebsites = this.websites.filter(w => w.status === 'active').length;
    this.stats.diskUsage = this.websites.reduce((sum, w) => sum + (w.disk_usage || 0), 0);

    // Mock recent activity
    this.recentActivity = this.websites.slice(0, 5).map(website => ({
      type: 'website_update',
      message: `Site ${website.name} mis à jour`,
      time: new Date(website.created_at),
      icon: 'fa-globe'
    }));
  }

  get diskUsagePercentage(): number {
    return (this.stats.diskUsage / this.stats.diskQuota) * 100;
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 MB';
    const k = 1024;
    const sizes = ['MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}
