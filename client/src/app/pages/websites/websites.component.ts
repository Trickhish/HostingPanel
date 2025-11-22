import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../api.service';
import { Website, WebsiteStatus } from '../../models/api.models';

@Component({
  selector: 'app-websites',
  imports: [CommonModule, RouterModule, FormsModule, TranslateModule],
  templateUrl: './websites.component.html',
  styleUrl: './websites.component.scss'
})
export class WebsitesComponent implements OnInit {
  websites: Website[] = [];
  filteredWebsites: Website[] = [];
  isLoading = true;
  isCreating = false;
  searchTerm = '';
  statusFilter: string = 'all';
  showCreateModal = false;
  createError = '';

  // New website form
  newWebsite = {
    name: '',
    domain: '',
    phpVersion: '8.2'
  };

  constructor(private apiService: ApiService) {
    
  }

  ngOnInit() {
    this.loadWebsites();
  }

  loadWebsites() {
    this.isLoading = true;
    this.apiService.getWebsites().subscribe({
      next: (response) => {
        if (response.success) {
          this.websites = response.websites;
          this.filterWebsites();
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading websites:', error);
        this.isLoading = false;
      }
    });
  }

  filterWebsites() {
    this.filteredWebsites = this.websites.filter(website => {
      const matchesSearch = website.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        website.site_path.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchesStatus = this.statusFilter === 'all' || website.status === this.statusFilter;
      return matchesSearch && matchesStatus;
    });
  }

  onSearchChange() {
    this.filterWebsites();
  }

  onStatusFilterChange() {
    this.filterWebsites();
  }

  openCreateModal() {
    this.showCreateModal = true;
  }

  closeCreateModal() {
    this.showCreateModal = false;
    this.createError = '';
    this.newWebsite = {
      name: '',
      domain: '',
      phpVersion: '8.2'
    };
  }

  createWebsite() {
    // Validate input
    if (!this.newWebsite.name || !this.newWebsite.name.trim()) {
      this.createError = 'Please enter a domain name';
      return;
    }

    // Validate domain format (must be like example.com)
    const domainPattern = /^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/;
    const domainName = this.newWebsite.name.trim().toLowerCase();

    if (!domainPattern.test(domainName)) {
      this.createError = 'Please enter a valid domain name (e.g., example.com)';
      return;
    }

    this.isCreating = true;
    this.createError = '';

    // Prepare request data
    const requestData = {
      name: domainName,
      php_version: this.newWebsite.phpVersion,
      install_wordpress: false
    };

    console.log('Sending create website request:', requestData);

    this.apiService.createWebsite(requestData).subscribe({
      next: (response) => {
        if (response.success) {
          console.log('Website created successfully:', response.website);
          // Close modal and reload websites
          this.closeCreateModal();
          this.loadWebsites();
        }
        this.isCreating = false;
      },
      error: (error) => {
        console.error('Error creating website:', error);
        console.error('Full error object:', error);

        // Handle different error formats
        let errorMessage = 'Failed to create website. Please try again.';

        if (error.error) {
          if (typeof error.error === 'string') {
            errorMessage = error.error;
          } else if (error.error.detail) {
            if (Array.isArray(error.error.detail)) {
              // Validation errors from FastAPI
              errorMessage = error.error.detail.map((e: any) => e.msg || e.message).join(', ');
            } else {
              errorMessage = error.error.detail;
            }
          } else if (error.error.message) {
            errorMessage = error.error.message;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }

        this.createError = errorMessage;
        this.isCreating = false;
      }
    });
  }

  getStatusClass(status: string): string {
    return status.toLowerCase();
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'active': return 'fa-check-circle';
      case 'installing': return 'fa-spinner fa-spin';
      case 'suspended': return 'fa-pause-circle';
      case 'error': return 'fa-exclamation-circle';
      default: return 'fa-circle';
    }
  }

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 MB';
    const k = 1024;
    const sizes = ['MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  get websiteStats() {
    return {
      total: this.websites.length,
      active: this.websites.filter(w => w.status === 'active').length,
      suspended: this.websites.filter(w => w.status === 'suspended').length,
      installing: this.websites.filter(w => w.status === 'installing').length
    };
  }
}
