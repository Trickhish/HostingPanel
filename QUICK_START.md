# Quick Start Guide - Authentication System

## What Was Created

Your HostingPanel application now has a complete authentication system integrated with your FastAPI backend:

### New Files Created

1. **Models & Interfaces**
   - `client/src/app/models/api.models.ts` - TypeScript interfaces for API data

2. **Services**
   - `client/src/app/services/auth.service.ts` - Authentication state management
   - `client/src/app/api.service.ts` - Updated with auth endpoints

3. **Guards**
   - `client/src/app/guards/auth.guard.ts` - Route protection (authGuard, adminGuard, guestGuard)

4. **Interceptors**
   - `client/src/app/interceptors/auth.interceptor.ts` - Auto-adds auth tokens to requests

5. **Configuration**
   - `client/src/environments/environment.ts` - Development config
   - `client/src/environments/environment.prod.ts` - Production config

6. **Documentation**
   - `AUTH_IMPLEMENTATION.md` - Complete technical documentation

### Modified Files

1. **Login Component** - Now fully functional with API integration
2. **App Routes** - Protected with auth guards
3. **App Config** - Registered HTTP interceptor
4. **Layout Component** - Added logout functionality

## How to Test

### 1. Create a Test User

First, make sure your backend is running, then create a test user:

```bash
cd server
python main.py
```

In another terminal, create a test user via the API:

```bash
curl -X POST http://localhost:21580/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "password123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

Or use any API client like Postman/Insomnia.

### 2. Start the Frontend

```bash
cd client
npm install  # If you haven't already
npm start
```

### 3. Test the Login Flow

1. Navigate to `http://localhost:4200`
2. You should be redirected to `/login` (thanks to authGuard)
3. Enter your test credentials:
   - Email: `admin@test.com`
   - Password: `password123`
4. Click "Continuer"
5. Upon successful login, you'll be redirected to `/dashboard`

### 4. Test Protected Routes

- Try accessing `/dashboard` - should work when logged in
- Try accessing `/settings` - should work when logged in
- Click logout - should redirect to `/login`
- Try accessing `/dashboard` again - should redirect to `/login`

### 5. Test the Logout

- Click the logout button in the sidebar (bottom)
- Should redirect to `/login`
- Token and user data cleared from localStorage

## Route Protection Examples

### Current Route Configuration

```
Public Routes (guestGuard):
  /login - Login page (redirects to /dashboard if already logged in)

Protected Routes (authGuard):
  /dashboard - Dashboard (requires authentication)
  /settings - Settings (requires authentication)
```

### Adding More Protected Routes

Edit `client/src/app/app.routes.ts`:

```typescript
// Regular protected route
{
  path: 'websites',
  loadComponent: () => import('./pages/websites/websites.component').then(m => m.WebsitesComponent),
  canActivate: [authGuard]
}

// Admin-only route
{
  path: 'admin/users',
  loadComponent: () => import('./pages/admin/users.component').then(m => m.AdminUsersComponent),
  canActivate: [adminGuard]
}
```

## Using Auth Service in Components

### Get Current User

```typescript
import { AuthService } from '../services/auth.service';

export class MyComponent {
  currentUser$ = this.authService.currentUser;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.currentUser$.subscribe(user => {
      console.log('Current user:', user);
      if (user) {
        console.log('Email:', user.email);
        console.log('Role:', user.role);
      }
    });
  }
}
```

### In Template

```html
<div *ngIf="authService.currentUser | async as user">
  <p>Welcome, {{ user.first_name }} {{ user.last_name }}!</p>
  <p>Email: {{ user.email }}</p>
  <p *ngIf="authService.isAdmin()">You are an admin!</p>
</div>
```

### Making Authenticated API Calls

```typescript
import { ApiService } from '../api.service';

export class WebsitesComponent {
  constructor(private apiService: ApiService) {}

  loadWebsites() {
    // Token automatically added by interceptor
    this.apiService.getWebsites().subscribe({
      next: (response) => {
        console.log('Websites:', response.websites);
      },
      error: (error) => {
        console.error('Error:', error);
      }
    });
  }
}
```

## Common Operations

### Check if User is Logged In

```typescript
if (this.authService.isAuthenticatedValue) {
  console.log('User is logged in');
}

// Or as Observable
this.authService.isAuthenticated.subscribe(isAuth => {
  console.log('Is authenticated:', isAuth);
});
```

### Check User Role

```typescript
if (this.authService.isAdmin()) {
  // Show admin features
}

if (this.authService.isClient()) {
  // Show client features
}
```

### Manual Logout

```typescript
logout() {
  this.authService.logout();
  // User will be redirected to /login automatically
}
```

## Debugging Tips

### View Stored Tokens

Open browser console and check localStorage:

```javascript
// View access token
localStorage.getItem('access_token')

// View refresh token
localStorage.getItem('refresh_token')

// View current user
localStorage.getItem('current_user')
```

### Network Tab

Open DevTools Network tab to see:
- Login request/response
- Authorization headers on protected requests
- Token refresh attempts on 401 errors

### Common Issues

**Issue**: "Network error" when logging in
- Check if backend is running on `http://localhost:21580`
- Check CORS settings in backend

**Issue**: "Unauthorized" errors on protected routes
- Check if token is being added in Network tab
- Check if interceptor is registered in app.config.ts
- Check token expiration

**Issue**: Redirect loop
- Check guard configuration
- Make sure login route has `guestGuard`
- Make sure protected routes have `authGuard`

## Next Steps

1. **Add Registration Page**
   - Create a registration component similar to login
   - Use `authService.register()` method

2. **Add User Profile Page**
   - Display current user information
   - Allow editing profile details

3. **Add Password Change**
   - Create form for password change
   - Use `apiService.changePassword()`

4. **Add Forgot Password Flow**
   - Create forgot password page
   - Create reset password page
   - Use `apiService.forgotPassword()` and `apiService.resetPassword()`

5. **Improve Error Handling**
   - Add more specific error messages
   - Add toast notifications for feedback

6. **Add Loading States**
   - Show spinners during API calls
   - Disable buttons during loading

## Backend API Reference

Your FastAPI backend provides these endpoints:

### Public Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Protected Endpoints (Token Required)
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user
- `POST /auth/change-password` - Change password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/api/websites` - Get user's websites

### Admin Endpoints (Admin Role Required)
- `GET /auth/api/admin/users` - Get all users

## Security Notes

For development, tokens are stored in localStorage. For production, consider:
- Using httpOnly cookies instead
- Implementing CSRF protection
- Adding rate limiting
- Using HTTPS only
- Setting appropriate token expiration times

See `AUTH_IMPLEMENTATION.md` for detailed security recommendations.
