import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../api.service';
import { Website, WebsiteStatus } from '../../models/api.models';

@Component({
  selector: 'app-websites',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './websites.component.html',
  styleUrl: './websites.component.scss'
})
export class WebsitesComponent implements OnInit {
  websites: Website[] = [];
  filteredWebsites: Website[] = [];
  isLoading = true;
  searchTerm = '';
  statusFilter: string = 'all';
  showCreateModal = false;

  // New website form
  newWebsite = {
    name: '',
    domain: '',
    phpVersion: '8.2'
  };

  constructor(private apiService: ApiService) {}

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
    this.newWebsite = {
      name: '',
      domain: '',
      phpVersion: '8.2'
    };
  }

  createWebsite() {
    // TODO: Implement website creation API call
    console.log('Creating website:', this.newWebsite);
    this.closeCreateModal();
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
