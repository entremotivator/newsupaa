"""
Application Configuration Settings
Enhanced Streamlit User Management System
"""

import os
from typing import Dict, List, Optional
from datetime import timedelta

class AppSettings:
    """Application configuration settings"""
    
    # Application Information
    APP_NAME = "User Management System"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Enhanced Streamlit application with user authentication and role-based access control"
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Authentication Settings
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    REQUIRE_EMAIL_VERIFICATION = os.getenv("REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true"
    REQUIRE_ADMIN_APPROVAL = os.getenv("REQUIRE_ADMIN_APPROVAL", "false").lower() == "true"
    
    # Rate Limiting
    API_RATE_LIMIT_PER_HOUR = int(os.getenv("API_RATE_LIMIT_PER_HOUR", "1000"))
    TOKEN_RATE_LIMIT_PER_HOUR = int(os.getenv("TOKEN_RATE_LIMIT_PER_HOUR", "10000"))
    FILE_UPLOAD_LIMIT_MB = int(os.getenv("FILE_UPLOAD_LIMIT_MB", "100"))
    
    # Feature Flags
    ENABLE_USER_REGISTRATION = os.getenv("ENABLE_USER_REGISTRATION", "true").lower() == "true"
    ENABLE_2FA = os.getenv("ENABLE_2FA", "true").lower() == "true"
    ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
    ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
    
    # UI/UX Settings
    THEME_PRIMARY_COLOR = os.getenv("THEME_PRIMARY_COLOR", "#4caf50")
    THEME_BACKGROUND_COLOR = os.getenv("THEME_BACKGROUND_COLOR", "#f1f8e9")
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))
    
    # Email Configuration
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
    
    # File Storage
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,pdf,txt,csv").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache Settings
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Security Settings
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"
    
    @classmethod
    def get_subscription_limits(cls) -> Dict[str, Dict[str, int]]:
        """Get subscription tier limits"""
        return {
            'free': {
                'monthly_tokens': int(os.getenv("FREE_MONTHLY_TOKENS", "10000")),
                'max_files': int(os.getenv("FREE_MAX_FILES", "5")),
                'max_threads': int(os.getenv("FREE_MAX_THREADS", "10")),
                'max_assistants': int(os.getenv("FREE_MAX_ASSISTANTS", "2")),
                'api_requests_per_hour': int(os.getenv("FREE_API_REQUESTS_PER_HOUR", "100"))
            },
            'pro': {
                'monthly_tokens': int(os.getenv("PRO_MONTHLY_TOKENS", "100000")),
                'max_files': int(os.getenv("PRO_MAX_FILES", "50")),
                'max_threads': int(os.getenv("PRO_MAX_THREADS", "100")),
                'max_assistants': int(os.getenv("PRO_MAX_ASSISTANTS", "10")),
                'api_requests_per_hour': int(os.getenv("PRO_API_REQUESTS_PER_HOUR", "1000"))
            },
            'enterprise': {
                'monthly_tokens': int(os.getenv("ENTERPRISE_MONTHLY_TOKENS", "1000000")),
                'max_files': int(os.getenv("ENTERPRISE_MAX_FILES", "500")),
                'max_threads': int(os.getenv("ENTERPRISE_MAX_THREADS", "1000")),
                'max_assistants': int(os.getenv("ENTERPRISE_MAX_ASSISTANTS", "50")),
                'api_requests_per_hour': int(os.getenv("ENTERPRISE_API_REQUESTS_PER_HOUR", "10000"))
            }
        }
    
    @classmethod
    def get_role_permissions(cls) -> Dict[str, List[str]]:
        """Get role-based permissions"""
        return {
            'user': [
                'view_dashboard',
                'edit_profile',
                'view_analytics',
                'use_api',
                'upload_files',
                'create_threads'
            ],
            'moderator': [
                'view_dashboard',
                'edit_profile',
                'view_analytics',
                'use_api',
                'upload_files',
                'create_threads',
                'moderate_content',
                'view_user_reports',
                'manage_user_content'
            ],
            'admin': [
                'view_dashboard',
                'edit_profile',
                'view_analytics',
                'use_api',
                'upload_files',
                'create_threads',
                'moderate_content',
                'view_user_reports',
                'manage_user_content',
                'manage_users',
                'view_admin_panel',
                'system_settings',
                'bulk_operations',
                'view_system_logs',
                'manage_subscriptions',
                'send_notifications'
            ]
        }
    
    @classmethod
    def get_notification_types(cls) -> List[str]:
        """Get available notification types"""
        return [
            'welcome',
            'email_verification',
            'password_reset',
            'account_approved',
            'account_rejected',
            'subscription_updated',
            'usage_limit_warning',
            'security_alert',
            'system_maintenance',
            'feature_announcement'
        ]
    
    @classmethod
    def get_activity_types(cls) -> List[str]:
        """Get trackable activity types"""
        return [
            'login',
            'logout',
            'profile_update',
            'password_change',
            'api_request',
            'file_upload',
            'chat_created',
            'assistant_created',
            'subscription_change',
            'settings_update',
            'admin_action',
            'bulk_operation',
            'error',
            'security_event'
        ]
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Check required environment variables
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_SERVICE_ROLE_KEY'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                errors.append(f"Missing required environment variable: {var}")
        
        # Validate numeric settings
        if cls.PASSWORD_MIN_LENGTH < 6:
            errors.append("PASSWORD_MIN_LENGTH must be at least 6")
        
        if cls.SESSION_TIMEOUT_HOURS < 1:
            errors.append("SESSION_TIMEOUT_HOURS must be at least 1")
        
        if cls.MAX_LOGIN_ATTEMPTS < 3:
            errors.append("MAX_LOGIN_ATTEMPTS must be at least 3")
        
        # Validate file settings
        if cls.FILE_UPLOAD_LIMIT_MB < 1:
            errors.append("FILE_UPLOAD_LIMIT_MB must be at least 1")
        
        if not cls.ALLOWED_FILE_TYPES:
            errors.append("ALLOWED_FILE_TYPES cannot be empty")
        
        return errors
    
    @classmethod
    def get_streamlit_config(cls) -> Dict:
        """Get Streamlit-specific configuration"""
        return {
            'page_title': cls.APP_NAME,
            'page_icon': '🔐',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded',
            'menu_items': {
                'Get Help': None,
                'Report a bug': None,
                'About': f"{cls.APP_NAME} v{cls.APP_VERSION}"
            }
        }
    
    @classmethod
    def get_database_config(cls) -> Dict:
        """Get database configuration"""
        return {
            'url': cls.SUPABASE_URL,
            'anon_key': cls.SUPABASE_ANON_KEY,
            'service_role_key': cls.SUPABASE_SERVICE_ROLE_KEY,
            'timeout': 30,
            'retry_attempts': 3
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == 'development'

# Create a global settings instance
settings = AppSettings()

# Validate configuration on import (only fail in production)
config_errors = settings.validate_config()
if config_errors and settings.is_production():
    raise ValueError(f"Configuration errors: {', '.join(config_errors)}")
elif config_errors and settings.DEBUG:
    # In debug mode, just print warnings
    print(f"⚠️  Configuration warnings: {', '.join(config_errors)}")
