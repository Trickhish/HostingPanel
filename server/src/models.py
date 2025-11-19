from datetime import datetime, timezone, timedelta, date

from src.utils import *

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse

from sqlalchemy import DateTime, Table, create_engine, Column, Integer, String, Boolean, ForeignKey, select, Enum as SQLEnum, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import func

from typing import List, Optional
from contextlib import asynccontextmanager
import os
from typing import List
from uuid import uuid4
import json
import asyncio
import enum

from werkzeug.security import generate_password_hash, check_password_hash

from src.database import Base

def jsonObject(inst):
    return({column.name: getattr(inst, column.name) for column in inst.__table__.columns})


class UserRole(enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))

    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)

    creation_date = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)

    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def reset_failed_login(self) -> bool:
        self.failed_login_attempts = 0
        return(True)

    def increment_failed_login(self):
        """Increment failed login attempts and lock account if threshold reached"""
        self.failed_login_attempts += 1
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_login_ip': self.last_login_ip,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'failed_login_attempts': self.failed_login_attempts,
        }


class UserSession(Base):
    """Track user sessions for security"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session data
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(255), unique=True, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))







class WebsiteStatus(enum.Enum):
    INSTALLING = "installing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    MIGRATING = "migrating"
    DELETING = "deleting"


class PHPVersion(enum.Enum):
    PHP_74 = "7.4"
    PHP_80 = "8.0"
    PHP_81 = "8.1"
    PHP_82 = "8.2"
    PHP_83 = "8.3"

class Website(Base):
    __tablename__ = "websites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(WebsiteStatus), default=WebsiteStatus.INSTALLING, nullable=False, index=True)
    site_path = Column(String(500), nullable=False)

    disk_quota = Column(Integer, nullable=True)
    disk_usage = Column(Integer, default=0, nullable=False)

    backup_enabled = Column(Boolean, default=True, nullable=False)
    backup_frequency = Column(String(20), default="daily", nullable=False)
    last_backup_at = Column(DateTime, nullable=True)
    backup_retention_days = Column(Integer, default=30, nullable=False)

    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    suspended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="websites")
    logs = relationship("ActivityLog", back_populates="website", cascade="all, delete-orphan")
    backups = relationship("Backup", back_populates="website", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status.value,
            'site_path': self.site_path,
            'disk_usage': self.disk_usage,
            'disk_quota': self.disk_quota,
            'backup_enabled': self.backup_enabled,
            'backup_frequency': self.backup_frequency,
            'backup_retention_days': self.backup_retention_days,
            'last_backup_at': self.last_backup_at.isoformat() if self.last_backup_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'suspended_at': self.suspended_at.isoformat() if self.suspended_at else None,
        }







class Backup(Base):
    __tablename__ = "backups"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False, index=True)
    website = relationship("Website", back_populates="backups")

    size = Column(Integer, default=0, nullable=False)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'website_id': self.website_id,
            'size': self.size,
            'is_encrypted': self.is_encrypted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }








class ActivityType(enum.Enum):
    """Types of activities to log"""
    # User activities
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    USER_PASSWORD_CHANGE = "user_password_change"
    USER_PASSWORD_RESET = "user_password_reset"
    USER_EMAIL_CHANGE = "user_email_change"
    USER_PROFILE_UPDATE = "user_profile_update"
    
    # Website activities
    WEBSITE_CREATE = "website_create"
    WEBSITE_DELETE = "website_delete"
    WEBSITE_SUSPEND = "website_suspend"
    WEBSITE_ACTIVATE = "website_activate"
    WEBSITE_UPDATE = "website_update"
    WEBSITE_MIGRATE = "website_migrate"
    
    # WordPress activities
    WP_INSTALL = "wp_install"
    WP_UPDATE = "wp_update"
    WP_PLUGIN_INSTALL = "wp_plugin_install"
    WP_PLUGIN_UPDATE = "wp_plugin_update"
    WP_PLUGIN_DELETE = "wp_plugin_delete"
    WP_PLUGIN_ACTIVATE = "wp_plugin_activate"
    WP_PLUGIN_DEACTIVATE = "wp_plugin_deactivate"
    WP_THEME_INSTALL = "wp_theme_install"
    WP_THEME_UPDATE = "wp_theme_update"
    WP_THEME_DELETE = "wp_theme_delete"
    WP_THEME_ACTIVATE = "wp_theme_activate"
    
    # Backup activities
    BACKUP_CREATE = "backup_create"
    BACKUP_DELETE = "backup_delete"
    BACKUP_RESTORE = "backup_restore"
    BACKUP_DOWNLOAD = "backup_download"
    
    # SSL activities
    SSL_INSTALL = "ssl_install"
    SSL_RENEW = "ssl_renew"
    SSL_REMOVE = "ssl_remove"
    
    # Security activities
    FIREWALL_ENABLE = "firewall_enable"
    FIREWALL_DISABLE = "firewall_disable"
    MALWARE_SCAN = "malware_scan"
    MALWARE_DETECTED = "malware_detected"
    MALWARE_CLEANED = "malware_cleaned"
    
    # System activities
    PHP_VERSION_CHANGE = "php_version_change"
    CACHE_CLEAR = "cache_clear"
    CACHE_ENABLE = "cache_enable"
    CACHE_DISABLE = "cache_disable"
    
    # Admin activities
    ADMIN_SETTING_CHANGE = "admin_setting_change"
    ADMIN_USER_CREATE = "admin_user_create"
    ADMIN_USER_DELETE = "admin_user_delete"
    ADMIN_USER_ROLE_CHANGE = "admin_user_role_change"

class ActivityLevel(enum.Enum):
    """Activity log levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ActivityLog(Base):
    """Activity log for all system activities"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (nullable because not all activities relate to a specific entity)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=True, index=True)
    
    # Activity information
    activity_type = Column(SQLEnum(ActivityType), nullable=False, index=True)
    level = Column(SQLEnum(ActivityLevel), default=ActivityLevel.INFO, nullable=False)
    
    # Description
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Technical details
    entity_type = Column(String(50), nullable=True)  # e.g., "website", "user", "backup"
    entity_id = Column(Integer, nullable=True)
    
    # Request information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_path = Column(String(500), nullable=True)
    
    # Additional metadata (JSON)
    data = Column(Text, nullable=True)  # Store as JSON string
    
    # Error information (for failed activities)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    website = relationship("Website", back_populates="logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, type='{self.activity_type.value}', level='{self.level.value}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'website_id': self.website_id,
            'activity_type': self.activity_type.value,
            'level': self.level.value,
            'title': self.title,
            'description': self.description,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ip_address': self.ip_address,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
        }


class TaskType(enum.Enum):
    """Types of background tasks"""
    WEBSITE_CREATE = "website_create"
    WEBSITE_DELETE = "website_delete"
    WEBSITE_MIGRATE = "website_migrate"
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"
    SSL_INSTALL = "ssl_install"
    SSL_RENEW = "ssl_renew"
    WP_INSTALL = "wp_install"
    WP_UPDATE = "wp_update"
    DATABASE_OPTIMIZE = "database_optimize"

class TaskStatus(enum.Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(Base):
    """Background task queue"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=True, index=True)

    task_type = Column(SQLEnum(TaskType), nullable=False, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)

    # Task details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Progress tracking
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    current_step = Column(String(255), nullable=True)
    total_steps = Column(Integer, default=1, nullable=False)

    # Task data and result
    input_data = Column(Text, nullable=True)  # JSON string
    result_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    website = relationship("Website")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'website_id': self.website_id,
            'task_type': self.task_type.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class HostingPlan(Base):
    """Hosting plans/subscriptions"""
    __tablename__ = "hosting_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    price = Column(Integer, nullable=False)  # Price in cents

    # Limits
    max_websites = Column(Integer, nullable=False)
    storage_gb = Column(Integer, nullable=False)
    bandwidth_gb = Column(Integer, nullable=False)

    # Features
    ssl_enabled = Column(Boolean, default=True, nullable=False)
    backups_enabled = Column(Boolean, default=True, nullable=False)
    staging_enabled = Column(Boolean, default=False, nullable=False)
    cdn_enabled = Column(Boolean, default=False, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price / 100,  # Convert cents to dollars
            'features': {
                'websites': self.max_websites,
                'storage': self.storage_gb,
                'bandwidth': self.bandwidth_gb,
                'ssl': self.ssl_enabled,
                'backups': self.backups_enabled,
                'staging': self.staging_enabled,
                'cdn': self.cdn_enabled,
            },
            'is_active': self.is_active,
        }


class Subscription(Base):
    """User hosting subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("hosting_plans.id"), nullable=False)

    status = Column(String(20), default="active", nullable=False)  # active, cancelled, suspended

    # Billing
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    plan = relationship("HostingPlan", back_populates="subscriptions")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Domain(Base):
    """External domains linked to websites"""
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=True, index=True)

    domain_name = Column(String(255), nullable=False, unique=True, index=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    # DNS verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(64), nullable=True)

    # SSL
    ssl_enabled = Column(Boolean, default=False, nullable=False)
    ssl_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    website = relationship("Website")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'website_id': self.website_id,
            'domain_name': self.domain_name,
            'is_primary': self.is_primary,
            'is_verified': self.is_verified,
            'ssl_enabled': self.ssl_enabled,
            'ssl_expires_at': self.ssl_expires_at.isoformat() if self.ssl_expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
        }