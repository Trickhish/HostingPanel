import { Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';
import { authGuard, guestGuard, adminGuard } from './guards/auth.guard';

export const routes: Routes = [
    // Public routes (only accessible when not authenticated)
    {
        path: 'login',
        loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent),
        canActivate: [guestGuard]
    },

    // Protected routes (require authentication)
    {
        path: '',
        component: LayoutComponent,
        canActivate: [authGuard],
        children: [
            {
                path: '',
                redirectTo: 'dashboard',
                pathMatch: 'full'
            },
            {
                path: 'dashboard',
                loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent)
            },
            {
                path: 'websites',
                loadComponent: () => import('./pages/websites/websites.component').then(m => m.WebsitesComponent)
            },
            {
                path: 'domains',
                loadComponent: () => import('./pages/domains/domains.component').then(m => m.DomainsComponent)
            },
            {
                path: 'hosting',
                loadComponent: () => import('./pages/hosting/hosting.component').then(m => m.HostingComponent)
            },
            {
                path: 'settings',
                loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent)
            }
        ]
    },

    // 404 - Must be last
    {
        path: '**',
        loadComponent: () => import('./pages/not-found/not-found.component').then(m => m.NotFoundComponent)
    }
];
