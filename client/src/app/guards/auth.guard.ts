import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticatedValue) {
    return true;
  }

  // Store the attempted URL for redirecting after login
  router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
  return false;
};

export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticatedValue && authService.isAdmin()) {
    return true;
  }

  if (!authService.isAuthenticatedValue) {
    router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
  } else {
    // User is authenticated but not admin
    router.navigate(['/dashboard']);
  }

  return false;
};

export const guestGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticatedValue) {
    return true;
  }

  // Already authenticated, redirect to dashboard
  router.navigate(['/dashboard']);
  return false;
};
