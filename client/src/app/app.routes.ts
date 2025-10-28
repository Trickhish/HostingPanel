import { Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';

export const routes: Routes = [
    // Redirect root to dashboard
    {
        path: '',
        redirectTo: '/dashboard',
        pathMatch: 'full'
    },

    {
        path: 'login',
        loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
    },


    {
        path: '',
        component: LayoutComponent,
        children: [
            {
                path: 'dashboard',
                loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent)
            },
            {
                path: 'settings',
                loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent)
            },
            /*{
                path: 'websites/create',
                loadComponent: () => import('./pages/websites/website-create/website-create.component').then(m => m.WebsiteCreateComponent)
            },
            {
                path: 'websites/:id',
                loadComponent: () => import('./pages/websites/website-detail/website-detail.component').then(m => m.WebsiteDetailComponent)
            },
            {
                path: 'backups',
                loadComponent: () => import('./pages/backups/backups.component').then(m => m.BackupsComponent)
            },
            {
                path: 'users',
                loadComponent: () => import('./pages/users/users.component').then(m => m.UsersComponent)
            },
            {
                path: 'settings',
                loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent)
            }*/


            {
                path: '**',
                loadComponent: () => import('./pages/not-found/not-found.component').then(m => m.NotFoundComponent)
            }
        ]
    },

    
    
];
