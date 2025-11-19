import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface Domain {
  id: number;
  name: string;
  status: 'active' | 'pending' | 'error';
  linkedWebsite?: string;
  sslEnabled: boolean;
  expiresAt: Date;
}

interface DomainProvider {
  name: string;
  logo: string;
  url: string;
  tutorial: string[];
}

@Component({
  selector: 'app-domains',
  imports: [CommonModule, FormsModule],
  templateUrl: './domains.component.html',
  styleUrl: './domains.component.scss'
})
export class DomainsComponent implements OnInit {
  domains: Domain[] = [];
  showAddModal = false;
  showTutorialModal = false;
  selectedProvider: DomainProvider | null = null;

  newDomain = {
    name: '',
    websiteId: null
  };

  popularProviders: DomainProvider[] = [
    {
      name: 'Namecheap',
      logo: 'https://www.namecheap.com/assets/img/nc-icon/nc-logo.svg',
      url: 'https://www.namecheap.com',
      tutorial: [
        'Connectez-vous à votre compte Namecheap',
        'Allez dans "Domain List" et sélectionnez votre domaine',
        'Cliquez sur "Manage" puis sur l\'onglet "Advanced DNS"',
        'Ajoutez un enregistrement A avec:',
        '  - Type: A Record',
        '  - Host: @',
        '  - Value: VOTRE_IP_SERVEUR',
        '  - TTL: Automatic',
        'Ajoutez un enregistrement A pour www avec:',
        '  - Type: A Record',
        '  - Host: www',
        '  - Value: VOTRE_IP_SERVEUR',
        '  - TTL: Automatic',
        'Sauvegardez les modifications. La propagation DNS peut prendre jusqu\'à 48h.'
      ]
    },
    {
      name: 'GoDaddy',
      logo: 'https://img.godaddy.com/p/godaddy-logo.svg',
      url: 'https://www.godaddy.com',
      tutorial: [
        'Connectez-vous à votre compte GoDaddy',
        'Allez dans "My Products" > "Domains"',
        'Cliquez sur votre domaine puis sur "DNS" ou "Manage DNS"',
        'Trouvez la section "Records"',
        'Modifiez l\'enregistrement A existant (@) ou ajoutez-en un:',
        '  - Type: A',
        '  - Name: @',
        '  - Value: VOTRE_IP_SERVEUR',
        '  - TTL: 600 seconds',
        'Ajoutez ou modifiez l\'enregistrement pour www:',
        '  - Type: A',
        '  - Name: www',
        '  - Value: VOTRE_IP_SERVEUR',
        '  - TTL: 600 seconds',
        'Cliquez sur "Save". La propagation DNS peut prendre jusqu\'à 48h.'
      ]
    },
    {
      name: 'OVH',
      logo: 'https://www.ovhcloud.com/sites/default/files/styles/large_screens_1x/public/2020-06/logo-ovhcloud.png',
      url: 'https://www.ovh.com',
      tutorial: [
        'Connectez-vous à votre espace client OVH',
        'Allez dans "Domaines" et sélectionnez votre domaine',
        'Cliquez sur l\'onglet "Zone DNS"',
        'Cliquez sur "Modifier en mode textuel" ou "Ajouter une entrée"',
        'Ajoutez un enregistrement A:',
        '  - Sous-domaine: (vide pour @)',
        '  - Type: A',
        '  - Cible: VOTRE_IP_SERVEUR',
        '  - TTL: Par défaut',
        'Ajoutez un enregistrement A pour www:',
        '  - Sous-domaine: www',
        '  - Type: A',
        '  - Cible: VOTRE_IP_SERVEUR',
        '  - TTL: Par défaut',
        'Validez les modifications. La propagation DNS peut prendre jusqu\'à 24h.'
      ]
    },
    {
      name: 'Cloudflare',
      logo: 'https://www.cloudflare.com/img/logo-web-badges/cf-logo-on-white-bg.svg',
      url: 'https://www.cloudflare.com',
      tutorial: [
        'Connectez-vous à votre compte Cloudflare',
        'Sélectionnez votre domaine dans le dashboard',
        'Allez dans l\'onglet "DNS"',
        'Cliquez sur "Add record"',
        'Créez un enregistrement A:',
        '  - Type: A',
        '  - Name: @',
        '  - IPv4 address: VOTRE_IP_SERVEUR',
        '  - Proxy status: Proxied (orange) ou DNS only (gris)',
        '  - TTL: Auto',
        'Créez un second enregistrement A pour www:',
        '  - Type: A',
        '  - Name: www',
        '  - IPv4 address: VOTRE_IP_SERVEUR',
        '  - Proxy status: Proxied (orange) ou DNS only (gris)',
        '  - TTL: Auto',
        'Sauvegardez. Avec Cloudflare, la propagation est généralement rapide (quelques minutes).'
      ]
    }
  ];

  constructor() {}

  ngOnInit() {
    this.loadDomains();
  }

  loadDomains() {
    // Mock data - replace with actual API call
    this.domains = [
      {
        id: 1,
        name: 'example.com',
        status: 'active',
        linkedWebsite: 'Mon Site WordPress',
        sslEnabled: true,
        expiresAt: new Date(2025, 11, 31)
      }
    ];
  }

  openAddModal() {
    this.showAddModal = true;
  }

  closeAddModal() {
    this.showAddModal = false;
    this.newDomain = {
      name: '',
      websiteId: null
    };
  }

  addDomain() {
    // TODO: Implement API call to add domain
    console.log('Adding domain:', this.newDomain);
    this.closeAddModal();
  }

  openTutorial(provider: DomainProvider) {
    this.selectedProvider = provider;
    this.showTutorialModal = true;
  }

  closeTutorialModal() {
    this.showTutorialModal = false;
    this.selectedProvider = null;
  }

  getStatusClass(status: string): string {
    return status;
  }

  getDaysUntilExpiry(expiresAt: Date): number {
    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }
}
