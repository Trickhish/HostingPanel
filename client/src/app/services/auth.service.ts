import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { ApiService } from '../api.service';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;
  private isAuthenticatedSubject: BehaviorSubject<boolean>;
  public isAuthenticated: Observable<boolean>;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {
    const storedUser = this.getStoredUser();
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser = this.currentUserSubject.asObservable();

    this.isAuthenticatedSubject = new BehaviorSubject<boolean>(!!storedUser && !!this.getAccessToken());
    this.isAuthenticated = this.isAuthenticatedSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  public get isAuthenticatedValue(): boolean {
    return this.isAuthenticatedSubject.value;
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.apiService.login(credentials).pipe(
      tap(response => {
        if (response.success) {
          this.setAuthData(response);
          this.currentUserSubject.next(response.user);
          this.isAuthenticatedSubject.next(true);
        }
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.apiService.register(data).pipe(
      tap(response => {
        if (response.success) {
          this.setAuthData(response);
          this.currentUserSubject.next(response.user);
          this.isAuthenticatedSubject.next(true);
        }
      }),
      catchError(error => {
        console.error('Registration error:', error);
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    // Call logout API
    this.apiService.logout().subscribe({
      next: () => {
        this.clearAuthData();
      },
      error: (error) => {
        console.error('Logout error:', error);
        // Clear auth data even if logout API fails
        this.clearAuthData();
      }
    });
  }

  refreshToken(): Observable<string> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.apiService.refreshToken(refreshToken).pipe(
      map(response => {
        if (response.success) {
          this.setAccessToken(response.access_token);
          return response.access_token;
        }
        throw new Error('Token refresh failed');
      }),
      catchError(error => {
        console.error('Token refresh error:', error);
        this.clearAuthData();
        return throwError(() => error);
      })
    );
  }

  loadCurrentUser(): Observable<User> {
    return this.apiService.getCurrentUser().pipe(
      tap(response => {
        if (response.success) {
          this.currentUserSubject.next(response.user);
          this.storeUser(response.user);
          this.isAuthenticatedSubject.next(true);
        }
      }),
      map(response => response.user),
      catchError(error => {
        console.error('Load user error:', error);
        this.clearAuthData();
        return throwError(() => error);
      })
    );
  }

  // Token management
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setAccessToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  private setRefreshToken(token: string): void {
    localStorage.setItem('refresh_token', token);
  }

  private setAuthData(response: AuthResponse): void {
    this.setAccessToken(response.tokens.access_token);
    this.setRefreshToken(response.tokens.refresh_token);
    this.storeUser(response.user);
  }

  private clearAuthData(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }

  private storeUser(user: User): void {
    localStorage.setItem('current_user', JSON.stringify(user));
  }

  private getStoredUser(): User | null {
    const userStr = localStorage.getItem('current_user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  // Role checking helpers
  isAdmin(): boolean {
    const user = this.currentUserValue;
    return user?.role === 'admin';
  }

  isClient(): boolean {
    const user = this.currentUserValue;
    return user?.role === 'client';
  }
}
