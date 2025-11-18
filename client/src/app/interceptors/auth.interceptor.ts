import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { catchError, switchMap, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const accessToken = authService.getAccessToken();

  // Skip adding token for login and register requests
  const isAuthEndpoint = req.url.includes('/auth/login') ||
                         req.url.includes('/auth/register') ||
                         req.url.includes('/auth/refresh');

  if (accessToken && !isAuthEndpoint) {
    // Clone the request and add the authorization header
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${accessToken}`
      }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // If we get a 401 error and we have a refresh token, try to refresh
      if (error.status === 401 && authService.getRefreshToken() && !isAuthEndpoint) {
        return authService.refreshToken().pipe(
          switchMap((newAccessToken) => {
            // Retry the request with the new token
            const clonedReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${newAccessToken}`
              }
            });
            return next(clonedReq);
          }),
          catchError((refreshError) => {
            // If refresh fails, logout the user
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }

      return throwError(() => error);
    })
  );
};
