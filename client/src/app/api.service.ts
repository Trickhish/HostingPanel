import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RefreshTokenRequest,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ApiResponse,
  User,
  Website
} from './models/api.models';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Auth endpoints
  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.baseUrl}/auth/login`, credentials);
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.baseUrl}/auth/register`, data);
  }

  logout(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.baseUrl}/auth/logout`, {});
  }

  refreshToken(refreshToken: string): Observable<{ success: boolean; access_token: string; token_type: string }> {
    return this.http.post<{ success: boolean; access_token: string; token_type: string }>(
      `${this.baseUrl}/auth/refresh`,
      { refresh_token: refreshToken }
    );
  }

  getCurrentUser(): Observable<{ success: boolean; user: User }> {
    return this.http.get<{ success: boolean; user: User }>(`${this.baseUrl}/auth/me`);
  }

  changePassword(data: ChangePasswordRequest): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.baseUrl}/auth/change-password`, data);
  }

  forgotPassword(data: ForgotPasswordRequest): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.baseUrl}/auth/forgot-password`, data);
  }

  resetPassword(data: ResetPasswordRequest): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.baseUrl}/auth/reset-password`, data);
  }

  // Website endpoints
  getWebsites(): Observable<{ success: boolean; websites: Website[] }> {
    return this.http.get<{ success: boolean; websites: Website[] }>(`${this.baseUrl}/auth/api/websites`);
  }

  // Admin endpoints
  getAllUsers(): Observable<{ success: boolean; users: User[] }> {
    return this.http.get<{ success: boolean; users: User[] }>(`${this.baseUrl}/auth/api/admin/users`);
  }
}
