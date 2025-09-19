import streamlit as st
import hashlib
import re
from typing import Tuple, Dict, Optional
from .database import init_service_client

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self):
        self.supabase = init_service_client()
    
    def login(self, email: str, password: str) -> Tuple[bool, Dict, str]:
        """
        Authenticate user login
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success, user_data, message)
        """
        try:
            # Validate input
            if not self._validate_email(email):
                return False, {}, "Invalid email format"
            
            if not password:
                return False, {}, "Password is required"
            
            # Attempt authentication with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Get user profile data
                user_data = self._get_user_profile(auth_response.user.id)
                
                # Update last login
                self._update_last_login(auth_response.user.id)
                
                return True, user_data, "Login successful!"
            else:
                return False, {}, "Invalid credentials"
                
        except Exception as e:
            error_message = str(e)
            if "Invalid login credentials" in error_message:
                return False, {}, "Invalid email or password"
            elif "Email not confirmed" in error_message:
                return False, {}, "Please verify your email address before logging in"
            else:
                return False, {}, f"Login failed: {error_message}"
    
    def signup(self, email: str, password: str, first_name: str, last_name: str) -> Tuple[bool, str]:
        """
        Register a new user
        
        Args:
            email: User email address
            password: User password
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            if not self._validate_email(email):
                return False, "Invalid email format"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters long"
            
            if not first_name or not last_name:
                return False, "First name and last name are required"
            
            # Check if user already exists
            existing_user = self.supabase.table("profiles").select("email").eq("email", email).execute()
            if existing_user.data:
                return False, "An account with this email already exists"
            
            # Create user with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": f"{first_name} {last_name}"
                    }
                }
            })
            
            if auth_response.user:
                # Create profile record
                profile_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "full_name": f"{first_name} {last_name}",
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "user",
                    "created_at": auth_response.user.created_at
                }
                
                # Insert into profiles table
                self.supabase.table("profiles").insert(profile_data).execute()
                
                # Create user preferences record
                preferences_data = {
                    "user_id": auth_response.user.id,
                    "theme": "light",
                    "language": "en",
                    "notifications": True,
                    "email_notifications": True
                }
                
                self.supabase.table("user_preferences").insert(preferences_data).execute()
                
                # Create users table record for extended data
                users_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "subscription_tier": "free",
                    "is_active": True,
                    "monthly_token_limit": 10000,
                    "tokens_used_this_month": 0,
                    "max_files": 5,
                    "max_threads": 10,
                    "voice_enabled": False,
                    "advanced_features": False,
                    "subscription_status": "active"
                }
                
                self.supabase.table("users").insert(users_data).execute()
                
                return True, "Account created successfully! Please check your email to verify your account."
            else:
                return False, "Failed to create account"
                
        except Exception as e:
            error_message = str(e)
            if "User already registered" in error_message:
                return False, "An account with this email already exists"
            elif "Password should be at least 6 characters" in error_message:
                return False, "Password must be at least 6 characters long"
            else:
                return False, f"Registration failed: {error_message}"
    
    def logout(self):
        """Log out the current user"""
        try:
            self.supabase.auth.sign_out()
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            return True, "Logged out successfully"
        except Exception as e:
            return False, f"Logout failed: {str(e)}"
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _get_user_profile(self, user_id: str) -> Dict:
        """Get comprehensive user profile data"""
        try:
            # Get profile data
            profile_response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            profile = profile_response.data[0] if profile_response.data else {}
            
            # Get user role
            role_response = self.supabase.table("user_roles").select("role").eq("user_id", user_id).execute()
            role = role_response.data[0]["role"] if role_response.data else profile.get("role", "user")
            
            # Get extended user data
            user_response = self.supabase.table("users").select("*").eq("id", user_id).execute()
            user_data = user_response.data[0] if user_response.data else {}
            
            # Get preferences
            prefs_response = self.supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
            preferences = prefs_response.data[0] if prefs_response.data else {}
            
            # Combine all data
            combined_data = {
                **profile,
                **user_data,
                "role": role,
                "preferences": preferences
            }
            
            return combined_data
            
        except Exception as e:
            st.error(f"Error fetching user profile: {str(e)}")
            return {}
    
    def _update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            from datetime import datetime
            
            # Update in users table
            self.supabase.table("users").update({
                "last_login": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            # Log activity
            activity_data = {
                "user_id": user_id,
                "activity_type": "login",
                "description": "User logged in",
                "created_at": datetime.now().isoformat()
            }
            
            self.supabase.table("user_activity_logs").insert(activity_data).execute()
            
        except Exception as e:
            # Don't fail login if logging fails
            pass
    
    def check_user_permissions(self, required_role: str = "user") -> bool:
        """Check if current user has required permissions"""
        if not st.session_state.get('authenticated', False):
            return False
        
        user_role = st.session_state.get('user_role', 'user')
        
        role_hierarchy = {
            'user': 1,
            'moderator': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 1)
        
        return user_level >= required_level
    
    def require_auth(self):
        """Decorator-like function to require authentication"""
        if not st.session_state.get('authenticated', False):
            st.error("🔒 Please log in to access this page")
            st.stop()
    
    def require_role(self, required_role: str):
        """Require specific role to access functionality"""
        self.require_auth()
        
        if not self.check_user_permissions(required_role):
            st.error(f"🚫 Access denied. This page requires {required_role} privileges.")
            st.stop()
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current user's ID"""
        user_data = st.session_state.get('user_data', {})
        return user_data.get('id')
    
    def get_current_user_role(self) -> str:
        """Get current user's role"""
        return st.session_state.get('user_role', 'user')
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.get_current_user_role() == 'admin'
