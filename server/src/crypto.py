import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from src.models import *
from src.database import *

load_dotenv()

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'qdshjkqsdkjhdfjhsdfhjksjhkuhqhhjk')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthService:
    @staticmethod
    def generate_access_token(user_id: int, email: str, role: str) -> str:
        """
        Generate JWT access token
        
        Args:
            user_id: User ID
            email: User email
            role: User role
            
        Returns:
            JWT access token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        """
        Generate JWT refresh token
        
        Args:
            user_id: User ID
            
        Returns:
            JWT refresh token string
        """
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            token_type: 'access' or 'refresh'
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get('type') != token_type:
                raise AuthError(f'Invalid token type. Expected {token_type}')
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError('Token has expired', 401)
        except jwt.InvalidTokenError:
            raise AuthError('Invalid token', 401)
    
    @staticmethod
    def register_user(
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: UserRole = UserRole.CLIENT
    ) -> Tuple[User, str, str]:
        """
        Register a new user
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            first_name: First name (optional)
            last_name: Last name (optional)
            role: User role (default: CLIENT)
            
        Returns:
            Tuple of (User object, access_token, refresh_token)
            
        Raises:
            AuthError: If user already exists or validation fails
        """
        with get_db() as db:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    raise AuthError('Email already registered', 400)
            
            # Validate password strength
            if len(password) < 8:
                raise AuthError('Password must be at least 8 characters long', 400)
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
                is_verified=False  # Set to True if you don't need email verification
            )
            user.set_password(password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.USER_REGISTER,
                level=ActivityLevel.INFO,
                title='User Registered',
                description=f'New user registered: {email}'
            )
            db.add(log)
            db.commit()
            
            # Generate tokens
            access_token = AuthService.generate_access_token(
                user.id, user.email, user.role.value
            )
            refresh_token = AuthService.generate_refresh_token(user.id)
            
            return user, access_token, refresh_token
    
    @staticmethod
    def login(
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        Login user and generate tokens
        
        Args:
            email: Email
            password: Plain text password
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
            
        Returns:
            Tuple of (User object, access_token, refresh_token)
            
        Raises:
            AuthError: If credentials are invalid or account is locked
        """
        with get_db() as db:
            user = db.query(User).filter(
                (User.email == email)
            ).first()
            
            if not user:
                raise AuthError('Invalid credentials', 401)
            
            # Check if account is locked
            if user.is_locked():
                minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
                raise AuthError(
                    f'Account is locked. Try again in {minutes_left} minutes',
                    403
                )
            
            # Check if account is active
            if not user.is_active:
                raise AuthError('Account is disabled', 403)
            
            # Verify password
            if not user.check_password(password):
                user.increment_failed_login()
                db.commit()
                
                raise AuthError('Invalid credentials', 401)
            
            # Reset failed login attempts
            user.reset_failed_login()
            user.last_login = datetime.utcnow()
            user.last_login_ip = ip_address
            db.commit()
            
            # Create session
            session = UserSession(
                user_id=user.id,
                session_token=AuthService.generate_refresh_token(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )
            db.add(session)
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.USER_LOGIN,
                level=ActivityLevel.INFO,
                title='User Login',
                description=f'User {user.first_name} logged in',
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(log)
            db.commit()
            
            # Generate tokens
            access_token = AuthService.generate_access_token(
                user.id, user.email, user.role.value
            )
            refresh_token = AuthService.generate_refresh_token(user.id)
            
            return user, access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthError: If refresh token is invalid
        """
        # Verify refresh token
        payload = AuthService.verify_token(refresh_token, 'refresh')
        user_id = payload.get('user_id')
        
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthError('User not found', 404)
            
            if not user.is_active:
                raise AuthError('Account is disabled', 403)
            
            # Generate new access token
            access_token = AuthService.generate_access_token(
                user.id, user.email, user.role.value
            )
            
            return access_token
    
    @staticmethod
    def logout(user_id: int, session_token: Optional[str] = None):
        """
        Logout user and invalidate session
        
        Args:
            user_id: User ID
            session_token: Session token to invalidate (optional)
        """
        with get_db() as db:
            # Delete specific session or all user sessions
            if session_token:
                db.query(UserSession).filter(
                    UserSession.user_id == user_id,
                    UserSession.session_token == session_token
                ).delete()
            else:
                # Delete all sessions for user
                db.query(UserSession).filter(
                    UserSession.user_id == user_id
                ).delete()
            
            # Log activity
            log = ActivityLog(
                user_id=user_id,
                activity_type=ActivityType.USER_LOGOUT,
                level=ActivityLevel.INFO,
                title='User Logout',
                description='User logged out'
            )
            db.add(log)
            db.commit()
    
    @staticmethod
    def get_current_user(token: str) -> User:
        """
        Get current user from access token
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            AuthError: If token is invalid or user not found
        """
        payload = AuthService.verify_token(token, 'access')
        user_id = payload.get('user_id')
        
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthError('User not found', 404)
            
            if not user.is_active:
                raise AuthError('Account is disabled', 403)
            
            return user
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Raises:
            AuthError: If old password is incorrect or validation fails
        """
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthError('User not found', 404)
            
            # Verify old password
            if not user.check_password(old_password):
                raise AuthError('Current password is incorrect', 401)
            
            # Validate new password
            if len(new_password) < 8:
                raise AuthError('Password must be at least 8 characters long', 400)
            
            # Set new password
            user.set_password(new_password)
            db.commit()
            
            # Log activity
            log = ActivityLog(
                user_id=user_id,
                activity_type=ActivityType.USER_PASSWORD_CHANGE,
                level=ActivityLevel.INFO,
                title='Password Changed',
                description='User changed their password'
            )
            db.add(log)
            db.commit()
    
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        """
        Generate password reset token
        
        Args:
            email: User email
            
        Returns:
            Password reset token
            
        Raises:
            AuthError: If user not found
        """
        with get_db() as db:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Don't reveal if email exists or not
                raise AuthError('If email exists, reset link will be sent', 200)
            
            # Generate reset token (expires in 1 hour)
            payload = {
                'user_id': user.id,
                'type': 'password_reset',
                'exp': datetime.utcnow() + timedelta(hours=1),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.USER_PASSWORD_RESET,
                level=ActivityLevel.INFO,
                title='Password Reset Requested',
                description='User requested password reset'
            )
            db.add(log)
            db.commit()
            
            return token
    
    @staticmethod
    def reset_password(token: str, new_password: str):
        """
        Reset password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Raises:
            AuthError: If token is invalid or validation fails
        """
        # Verify token
        payload = AuthService.verify_token(token, 'password_reset')
        user_id = payload.get('user_id')
        
        # Validate new password
        if len(new_password) < 8:
            raise AuthError('Password must be at least 8 characters long', 400)
        
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise AuthError('User not found', 404)
            
            # Set new password
            user.set_password(new_password)
            
            # Invalidate all sessions
            db.query(UserSession).filter(UserSession.user_id == user_id).delete()
            
            db.commit()
            
            # Log activity
            log = ActivityLog(
                user_id=user_id,
                activity_type=ActivityType.USER_PASSWORD_RESET,
                level=ActivityLevel.INFO,
                title='Password Reset',
                description='User reset their password'
            )
            db.add(log)
            db.commit()


# Decorator functions for route protection

def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return {'message': f'Hello {current_user.email}'}
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        from flask import request
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                raise AuthError('Invalid token format. Use: Bearer <token>')
        
        if not token:
            raise AuthError('Token is missing', 401)
        
        try:
            # Get current user
            current_user = AuthService.get_current_user(token)
            return f(current_user, *args, **kwargs)
            
        except AuthError as e:
            raise e
    
    return decorated


def role_required(*roles):
    """
    Decorator to restrict access based on user roles
    
    Usage:
        @app.route('/admin')
        @token_required
        @role_required(UserRole.ADMIN)
        def admin_route(current_user):
            return {'message': 'Admin only'}
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                raise AuthError('Insufficient permissions', 403)
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    """
    Decorator to restrict access to admins only
    
    Usage:
        @app.route('/admin')
        @token_required
        @admin_required
        def admin_route(current_user):
            return {'message': 'Admin only'}
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            raise AuthError('Admin access required', 403)
        return f(current_user, *args, **kwargs)
    return decorated


# Utility functions

def extract_token_from_header(authorization_header: str) -> str:
    """
    Extract JWT token from Authorization header
    
    Args:
        authorization_header: Authorization header value
        
    Returns:
        JWT token string
        
    Raises:
        AuthError: If header format is invalid
    """
    if not authorization_header:
        raise AuthError('Authorization header is missing', 401)
    
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise AuthError('Invalid authorization header format. Use: Bearer <token>', 401)
    
    return parts[1]


def get_token_payload(token: str) -> Dict[str, Any]:
    """
    Decode token without verification (useful for debugging)
    
    Args:
        token: JWT token
        
    Returns:
        Token payload dict
    """
    return jwt.decode(token, options={"verify_signature": False})