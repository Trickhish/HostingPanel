# Authentication System Implementation

This document explains the authentication system implementation for the HostingPanel application.

## Overview

The authentication system is built using Angular 20 on the frontend and FastAPI on the backend, implementing JWT token-based authentication with refresh token support.

## Architecture

### Backend (FastAPI)

Located in `/server/routes/auth.py`, the backend provides:

- **Login/Registration**: `/auth/login`, `/auth/register`
- **Token Management**: `/auth/refresh`, `/auth/logout`
- **Password Management**: `/auth/change-password`, `/auth/forgot-password`, `/auth/reset-password`
- **User Info**: `/auth/me`
- **Protected Routes**: Using `get_current_user` dependency

### Frontend (Angular)

The frontend authentication system consists of several key components:

#### 1. API Models (`/client/src/app/models/api.models.ts`)

TypeScript interfaces matching the FastAPI backend models:
- `User`, `UserRole`
- `LoginRequest`, `RegisterRequest`
- `TokenResponse`, `AuthResponse`
- `Website`, `WebsiteStatus`

#### 2. API Service (`/client/src/app/api.service.ts`)

Handles all HTTP communication with the backend:
- `login()` - Authenticate user
- `register()` - Register new user
- `logout()` - End user session
- `refreshToken()` - Refresh access token
- `getCurrentUser()` - Get current user info
- `getWebsites()` - Get user's websites (protected)

#### 3. Auth Service (`/client/src/app/services/auth.service.ts`)

Manages authentication state and tokens:
- **State Management**: Uses RxJS `BehaviorSubject` for reactive state
  - `currentUser`: Observable of current user
  - `isAuthenticated`: Observable of auth status
- **Token Storage**: localStorage for access/refresh tokens and user data
- **Token Refresh**: Automatic token refresh on expiration
- **User Management**: Login, logout, registration
- **Role Checking**: `isAdmin()`, `isClient()` helpers

#### 4. HTTP Interceptor (`/client/src/app/interceptors/auth.interceptor.ts`)

Automatically handles authentication for all HTTP requests:
- Adds `Authorization: Bearer <token>` header to protected requests
- Automatically attempts token refresh on 401 errors
- Retries failed requests after successful token refresh
- Logs out user if token refresh fails

#### 5. Auth Guards (`/client/src/app/guards/auth.guard.ts`)

Three guards for route protection:

- **`authGuard`**: Protects routes requiring authentication
  - Redirects to `/login` if not authenticated
  - Stores intended URL for redirect after login

- **`adminGuard`**: Protects admin-only routes
  - Requires authentication AND admin role
  - Redirects to `/login` if not authenticated
  - Redirects to `/dashboard` if authenticated but not admin

- **`guestGuard`**: For login/register pages
  - Prevents authenticated users from accessing
  - Redirects authenticated users to `/dashboard`

#### 6. Login Component (`/client/src/app/pages/login/login.component.ts`)

Fully functional login page:
- Form validation
- Error display with icons
- Password visibility toggle
- Loading state during authentication
- Return URL support for post-login redirect
- Integration with AuthService

## Usage Examples

### Protecting Routes

```typescript
// In app.routes.ts

// Public route (guest only)
{
  path: 'login',
  component: LoginComponent,
  canActivate: [guestGuard]
}

// Protected route (requires authentication)
{
  path: 'dashboard',
  component: DashboardComponent,
  canActivate: [authGuard]
}

// Admin-only route
{
  path: 'admin/users',
  component: UsersComponent,
  canActivate: [adminGuard]
}
```

### Using Auth Service in Components

```typescript
import { AuthService } from './services/auth.service';

export class MyComponent {
  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Subscribe to authentication state
    this.authService.isAuthenticated.subscribe(isAuth => {
      console.log('Authenticated:', isAuth);
    });

    // Get current user
    this.authService.currentUser.subscribe(user => {
      console.log('Current user:', user);
    });

    // Check if user is admin
    if (this.authService.isAdmin()) {
      // Show admin features
    }
  }

  logout() {
    this.authService.logout();
  }
}
```

### Making Authenticated API Calls

```typescript
import { ApiService } from './api.service';

export class WebsitesComponent {
  constructor(private apiService: ApiService) {}

  loadWebsites() {
    // The auth interceptor automatically adds the token
    this.apiService.getWebsites().subscribe({
      next: (response) => {
        console.log('Websites:', response.websites);
      },
      error: (error) => {
        console.error('Error loading websites:', error);
      }
    });
  }
}
```

## Security Features

### Token Management
- **Access Token**: Short-lived JWT token (automatically attached to requests)
- **Refresh Token**: Long-lived token for obtaining new access tokens
- **Automatic Refresh**: Interceptor automatically refreshes expired tokens
- **Secure Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)

### Route Protection
- **Auth Guard**: Prevents unauthorized access to protected routes
- **Guest Guard**: Prevents authenticated users from accessing login page
- **Admin Guard**: Role-based access control for admin features

### Error Handling
- **401 Unauthorized**: Automatic token refresh attempt
- **Failed Refresh**: Automatic logout and redirect to login
- **Network Errors**: User-friendly error messages

## Configuration

### Environment Variables

Edit `/client/src/environments/environment.ts` for development:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:21580'
};
```

Edit `/client/src/environments/environment.prod.ts` for production:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-domain.com'
};
```

## Flow Diagrams

### Login Flow
```
1. User enters credentials → LoginComponent
2. LoginComponent calls AuthService.login()
3. AuthService calls ApiService.login()
4. Backend validates credentials
5. Backend returns tokens + user data
6. AuthService stores tokens and user in localStorage
7. AuthService updates BehaviorSubjects (currentUser, isAuthenticated)
8. Router navigates to returnUrl or /dashboard
```

### Protected Route Access Flow
```
1. User navigates to protected route
2. authGuard checks AuthService.isAuthenticatedValue
3. If authenticated → allow access
4. If not authenticated → redirect to /login with returnUrl
```

### Authenticated API Request Flow
```
1. Component calls ApiService method
2. HTTP Interceptor adds Authorization header
3. Request sent to backend
4. If 401 error:
   a. Interceptor calls AuthService.refreshToken()
   b. If refresh succeeds: retry request with new token
   c. If refresh fails: logout and redirect to login
5. Return response to component
```

## Testing

### Creating a Test User

You can create a test user via the backend or registration endpoint:

```bash
# Using the API
curl -X POST http://localhost:21580/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Testing the Login

1. Start the backend: `cd server && python main.py`
2. Start the frontend: `cd client && npm start`
3. Navigate to `http://localhost:4200/login`
4. Enter test credentials
5. Should redirect to dashboard upon successful login

## Next Steps

### Recommended Improvements

1. **Add Registration Page**: Create a registration component similar to login
2. **Add Logout Button**: Add logout functionality to the layout component
3. **Add User Profile**: Create a page to view/edit user profile
4. **Password Reset Flow**: Implement forgot password UI
5. **Remember Me**: Add checkbox to extend session duration
6. **Session Timeout Warning**: Warn users before token expires
7. **Better Error Messages**: Translate error messages to French
8. **Loading States**: Add loading spinners for better UX

### Security Considerations for Production

1. **Use HttpOnly Cookies**: Store tokens in httpOnly cookies instead of localStorage
2. **CSRF Protection**: Implement CSRF tokens for state-changing operations
3. **Rate Limiting**: Add rate limiting on login endpoint
4. **Account Lockout**: Implement account lockout after failed attempts (already in backend)
5. **SSL/TLS**: Use HTTPS in production
6. **Token Expiration**: Set appropriate expiration times for tokens
7. **Secure Headers**: Add security headers (CSP, HSTS, etc.)

## Troubleshooting

### Common Issues

**Issue**: "CORS error when calling API"
- **Solution**: Ensure backend CORS middleware allows frontend origin

**Issue**: "Token not being sent with requests"
- **Solution**: Check that auth interceptor is registered in app.config.ts

**Issue**: "Redirect loop after login"
- **Solution**: Check that authGuard and guestGuard are properly configured

**Issue**: "User logged out unexpectedly"
- **Solution**: Check token expiration times and refresh token logic

## API Endpoints Reference

### Public Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Protected Endpoints (Require Authentication)
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user
- `POST /auth/change-password` - Change password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/api/websites` - Get user's websites

### Admin Endpoints (Require Admin Role)
- `GET /auth/api/admin/users` - Get all users
