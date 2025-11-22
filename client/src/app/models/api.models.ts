// User models
export enum UserRole {
  ADMIN = 'admin',
  CLIENT = 'client'
}

export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  last_login_ip?: string;
  creation_date?: string;
  failed_login_attempts?: number;
}

// Auth request/response models
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user: User;
  tokens: TokenResponse;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

// API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// Website models
export enum WebsiteStatus {
  INSTALLING = 'installing',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  ERROR = 'error',
  MIGRATING = 'migrating',
  DELETING = 'deleting'
}

export interface Website {
  id: number;
  user_id: number;
  name: string;
  status: WebsiteStatus;
  site_path: string;
  disk_usage: number;
  disk_quota?: number;
  backup_enabled: boolean;
  backup_frequency: string;
  backup_retention_days: number;
  last_backup_at?: string;
  created_at: string;
  suspended_at?: string;
}

export interface CreateWebsiteRequest {
  name: string;
  php_version?: string;
  install_wordpress?: boolean;
}
