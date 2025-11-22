import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../api.service';
import { AuthService } from '../../services/auth.service';

interface HostingPlan {
  name: string;
  price: number;
  features: {
    websites: number;
    storage: number; // in GB
    bandwidth: number; // in GB
    ssl: boolean;
    backups: boolean;
    support: string;
  };
  currentUsage: {
    websites: number;
    storage: number;
    bandwidth: number;
  };
}

@Component({
  selector: 'app-hosting',
  imports: [CommonModule, TranslateModule],
  templateUrl: './hosting.component.html',
  styleUrl: './hosting.component.scss'
})
export class HostingComponent implements OnInit {
  currentPlan: HostingPlan = {
    name: 'Starter',
    price: 9.99,
    features: {
      websites: 5,
      storage: 10,
      bandwidth: 100,
      ssl: true,
      backups: true,
      support: 'Email'
    },
    currentUsage: {
      websites: 0,
      storage: 0,
      bandwidth: 0
    }
  };

  availablePlans: HostingPlan[] = [
    {
      name: 'Starter',
      price: 9.99,
      features: {
        websites: 5,
        storage: 10,
        bandwidth: 100,
        ssl: true,
        backups: true,
        support: 'Email'
      },
      currentUsage: { websites: 0, storage: 0, bandwidth: 0 }
    },
    {
      name: 'Professional',
      price: 19.99,
      features: {
        websites: 25,
        storage: 50,
        bandwidth: 500,
        ssl: true,
        backups: true,
        support: 'Email & Chat'
      },
      currentUsage: { websites: 0, storage: 0, bandwidth: 0 }
    },
    {
      name: 'Business',
      price: 39.99,
      features: {
        websites: 100,
        storage: 200,
        bandwidth: 2000,
        ssl: true,
        backups: true,
        support: 'Priority 24/7'
      },
      currentUsage: { websites: 0, storage: 0, bandwidth: 0 }
    }
  ];

  websites: any[] = [];
  isLoading = true;

  constructor(
    private apiService: ApiService,
    public authService: AuthService
  ) {}

  ngOnInit() {
    this.loadHostingData();
  }

  loadHostingData() {
    this.isLoading = true;

    this.apiService.getWebsites().subscribe({
      next: (response) => {
        if (response.success) {
          this.websites = response.websites;
          this.calculateUsage();
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading hosting data:', error);
        this.isLoading = false;
      }
    });
  }

  calculateUsage() {
    this.currentPlan.currentUsage.websites = this.websites.length;
    this.currentPlan.currentUsage.storage = this.websites.reduce((sum, w) => sum + (w.disk_usage || 0), 0) / 1024; // Convert to GB
    // Bandwidth would need to be calculated from actual usage data
    this.currentPlan.currentUsage.bandwidth = Math.random() * 50; // Mock data
  }

  getUsagePercentage(used: number, limit: number): number {
    return (used / limit) * 100;
  }

  getUsageClass(percentage: number): string {
    if (percentage >= 90) return 'danger';
    if (percentage >= 70) return 'warning';
    return 'success';
  }

  isCurrentPlan(plan: HostingPlan): boolean {
    return plan.name === this.currentPlan.name;
  }

  getNextPaymentDate(): Date {
    const today = new Date();
    return new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
  }
}
