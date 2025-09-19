import streamlit as st
import os
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from datetime import datetime

@st.cache_resource
def init_service_client():
    """Initialize Supabase service role client with caching"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        service_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not service_key:
            st.error("❌ Missing Supabase configuration. Please check your secrets.toml file.")
            st.stop()
        
        client = create_client(url, service_key)
        # Test connection with a simple query
        test_response = client.table("profiles").select("id").limit(1).execute()
        
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to initialize service client: {str(e)}")
        st.stop()

@st.cache_resource
def init_client():
    """Initialize regular Supabase client with caching"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        anon_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not anon_key:
            st.error("❌ Missing Supabase configuration. Please check your secrets.toml file.")
            st.stop()
        
        client = create_client(url, anon_key)
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to initialize client: {str(e)}")
        st.stop()

class DatabaseManager:
    """Handles database operations and queries"""
    
    def __init__(self, use_service_role: bool = False):
        self.client = init_service_client() if use_service_role else init_client()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching user profile: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, data: Dict) -> bool:
        """Update user profile"""
        try:
            response = self.client.table("profiles").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        try:
            response = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            st.error(f"Error fetching preferences: {str(e)}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            # Check if preferences exist
            existing = self.client.table("user_preferences").select("user_id").eq("user_id", user_id).execute()
            
            if existing.data:
                # Update existing preferences
                response = self.client.table("user_preferences").update(preferences).eq("user_id", user_id).execute()
            else:
                # Insert new preferences
                preferences["user_id"] = user_id
                response = self.client.table("user_preferences").insert(preferences).execute()
            
            return True
        except Exception as e:
            st.error(f"Error updating preferences: {str(e)}")
            return False
    
    def get_user_usage_stats(self, user_id: str) -> Dict:
        """Get user usage statistics"""
        try:
            # Get API usage
            api_response = self.client.table("api_usage").select("*").eq("user_id", user_id).execute()
            api_data = api_response.data if api_response.data else []
            
            # Calculate totals
            total_tokens = sum([usage.get('total_tokens', 0) for usage in api_data])
            total_cost = sum([float(usage.get('cost', 0)) for usage in api_data])
            total_requests = len(api_data)
            
            # Get chat threads count
            threads_response = self.client.table("chat_threads").select("id").eq("user_id", user_id).execute()
            threads_count = len(threads_response.data) if threads_response.data else 0
            
            # Get file uploads count
            files_response = self.client.table("file_uploads").select("id").eq("user_id", user_id).execute()
            files_count = len(files_response.data) if files_response.data else 0
            
            # Get custom assistants count
            assistants_response = self.client.table("custom_assistants").select("id").eq("user_id", user_id).execute()
            assistants_count = len(assistants_response.data) if assistants_response.data else 0
            
            return {
                'total_tokens': total_tokens,
                'total_cost': total_cost,
                'total_requests': total_requests,
                'chat_threads_count': threads_count,
                'file_uploads_count': files_count,
                'custom_assistants_count': assistants_count
            }
            
        except Exception as e:
            st.error(f"Error fetching usage stats: {str(e)}")
            return {}
    
    def get_user_activity_logs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user activity logs"""
        try:
            response = self.client.table("user_activity_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching activity logs: {str(e)}")
            return []
    
    def log_user_activity(self, user_id: str, activity_type: str, description: str, metadata: Dict = None) -> bool:
        """Log user activity"""
        try:
            activity_data = {
                "user_id": user_id,
                "activity_type": activity_type,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }
            
            response = self.client.table("user_activity_logs").insert(activity_data).execute()
            return True
        except Exception as e:
            # Don't show error to user for logging failures
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users with comprehensive data (admin only)"""
        try:
            # Get auth users
            auth_response = self.client.auth.admin.list_users()
            
            # Handle different response formats
            auth_users = []
            if hasattr(auth_response, 'data') and hasattr(auth_response.data, 'users'):
                auth_users = auth_response.data.users
            elif hasattr(auth_response, 'users'):
                auth_users = auth_response.users
            elif isinstance(auth_response, list):
                auth_users = auth_response
            
            # Get data from all tables
            tables_data = {}
            
            for table_name in ['profiles', 'user_roles', 'user_profiles', 'users', 'pending_signups', 
                             'user_preferences', 'user_activity_logs', 'api_usage', 'chat_threads', 
                             'file_uploads', 'custom_assistants']:
                try:
                    response = self.client.table(table_name).select("*").execute()
                    tables_data[table_name] = response.data if response.data else []
                except:
                    tables_data[table_name] = []
            
            # Process and combine user data
            users = []
            for user in auth_users:
                try:
                    user_id = getattr(user, 'id', '')
                    user_email = getattr(user, 'email', '')
                    
                    if not user_id or not user_email:
                        continue
                    
                    # Combine data from all tables
                    user_data = self._combine_user_data(user, tables_data)
                    users.append(user_data)
                    
                except Exception as user_error:
                    continue
            
            return users
            
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []
    
    def _combine_user_data(self, auth_user, tables_data: Dict) -> Dict:
        """Combine user data from multiple tables"""
        user_id = getattr(auth_user, 'id', '')
        
        # Create lookup dictionaries
        profiles = {p['id']: p for p in tables_data['profiles']}
        user_roles = {r['user_id']: r['role'] for r in tables_data['user_roles']}
        user_profiles = {up['user_id']: up for up in tables_data['user_profiles']}
        users_table = {u['id']: u for u in tables_data['users']}
        pending_signups = {ps['email']: ps for ps in tables_data['pending_signups']}
        user_preferences = {up['user_id']: up for up in tables_data['user_preferences']}
        
        # Get user-specific data
        profile = profiles.get(user_id, {})
        user_profile = user_profiles.get(user_id, {})
        user_table_data = users_table.get(user_id, {})
        role = user_roles.get(user_id, profile.get('role', 'user'))
        preferences = user_preferences.get(user_id, {})
        
        # Calculate activity and usage stats
        user_activities = [a for a in tables_data['user_activity_logs'] if a['user_id'] == user_id]
        user_api_usage = [u for u in tables_data['api_usage'] if u['user_id'] == user_id]
        user_threads = [t for t in tables_data['chat_threads'] if t['user_id'] == user_id]
        user_files = [f for f in tables_data['file_uploads'] if f['user_id'] == user_id]
        user_assistants = [a for a in tables_data['custom_assistants'] if a['user_id'] == user_id]
        
        # Calculate usage totals
        total_tokens = sum([usage.get('total_tokens', 0) for usage in user_api_usage])
        total_cost = sum([float(usage.get('cost', 0)) for usage in user_api_usage])
        
        # Combine all data
        return {
            'id': user_id,
            'email': getattr(auth_user, 'email', ''),
            'created_at': getattr(auth_user, 'created_at', ''),
            'email_confirmed_at': getattr(auth_user, 'email_confirmed_at', None),
            'last_sign_in_at': getattr(auth_user, 'last_sign_in_at', None),
            'role': role,
            'full_name': profile.get('full_name', ''),
            'avatar_url': profile.get('avatar_url', ''),
            'website': profile.get('website', ''),
            'username': profile.get('username', ''),
            'updated_at': profile.get('updated_at', ''),
            'is_active': user_table_data.get('is_active', True),
            'subscription_tier': user_table_data.get('subscription_tier', 'free'),
            'tokens_used': total_tokens,
            'total_cost': total_cost,
            'monthly_token_limit': user_table_data.get('monthly_token_limit', 10000),
            'max_files': user_table_data.get('max_files', 5),
            'max_threads': user_table_data.get('max_threads', 10),
            'voice_enabled': user_table_data.get('voice_enabled', False),
            'advanced_features': user_table_data.get('advanced_features', False),
            'subscription_status': user_table_data.get('subscription_status', 'active'),
            'theme': preferences.get('theme', 'light'),
            'language': preferences.get('language', 'en'),
            'notifications': preferences.get('notifications', True),
            'email_notifications': preferences.get('email_notifications', True),
            'activity_logs_count': len(user_activities),
            'api_requests': len(user_api_usage),
            'chat_threads_count': len(user_threads),
            'file_uploads_count': len(user_files),
            'custom_assistants_count': len(user_assistants),
            'recent_activities': user_activities[-5:] if user_activities else []
        }
    
    def approve_user(self, user_id: str, email: str) -> bool:
        """Approve a pending user"""
        try:
            # Update pending_signups
            self.client.table("pending_signups").update({
                "status": "approved"
            }).eq("email", email).execute()
            
            # Update user_profiles if exists
            self.client.table("user_profiles").update({
                "status": "approved"
            }).eq("user_id", user_id).execute()
            
            return True
        except Exception as e:
            st.error(f"Error approving user: {str(e)}")
            return False
    
    def reject_user(self, user_id: str, email: str) -> bool:
        """Reject a pending user"""
        try:
            # Update pending_signups
            self.client.table("pending_signups").update({
                "status": "rejected"
            }).eq("email", email).execute()
            
            # Update user_profiles if exists
            self.client.table("user_profiles").update({
                "status": "rejected"
            }).eq("user_id", user_id).execute()
            
            return True
        except Exception as e:
            st.error(f"Error rejecting user: {str(e)}")
            return False
    
    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role"""
        try:
            # Check if role record exists
            existing = self.client.table("user_roles").select("user_id").eq("user_id", user_id).execute()
            
            if existing.data:
                # Update existing role
                self.client.table("user_roles").update({"role": new_role}).eq("user_id", user_id).execute()
            else:
                # Insert new role
                self.client.table("user_roles").insert({
                    "user_id": user_id,
                    "role": new_role
                }).execute()
            
            # Also update in profiles table
            self.client.table("profiles").update({"role": new_role}).eq("id", user_id).execute()
            
            return True
        except Exception as e:
            st.error(f"Error updating user role: {str(e)}")
            return False
