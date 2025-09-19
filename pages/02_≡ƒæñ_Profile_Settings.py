import streamlit as st
import sys
import os

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.auth import AuthManager
from components.database import DatabaseManager
from components.ui_components import (
    load_custom_css, show_alert, create_dashboard_card, 
    show_confirmation_dialog, safe_date_format
)
from components.utils import (
    validate_email, validate_password, sanitize_input, 
    get_user_avatar_url, log_user_action
)
from typing import Dict

# Page configuration
st.set_page_config(
    page_title="Profile Settings",
    page_icon="👤",
    layout="wide"
)

def main():
    """Main profile settings page"""
    
    # Load custom styling
    load_custom_css()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Require authentication
    auth_manager.require_auth()
    
    # Get current user data
    user_data = st.session_state.get('user_data', {})
    user_id = auth_manager.get_current_user_id()
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Page header
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="color: #2e7d32; margin-bottom: 0.5rem;">👤 Profile Settings</h1>
        <p style="color: #666; font-size: 1.1rem;">Manage your account information and preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal Info", "🔒 Security", "⚙️ Preferences", "📊 Account Details"])
    
    with tab1:
        show_personal_info_section(user_data, db, user_id)
    
    with tab2:
        show_security_section(user_data, auth_manager)
    
    with tab3:
        show_preferences_section(user_data, db, user_id)
    
    with tab4:
        show_account_details_section(user_data)

def show_personal_info_section(user_data: Dict, db: DatabaseManager, user_id: str):
    """Show personal information editing section"""
    
    st.markdown("### 👤 Personal Information")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Avatar section
        avatar_url = get_user_avatar_url(user_data)
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <img src="{avatar_url}" style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid #4caf50;">
            <p style="margin-top: 10px; color: #666;">Profile Picture</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Avatar upload placeholder
        st.info("Avatar upload functionality would be implemented here with file upload and image processing.")
    
    with col2:
        # Personal info form
        with st.form("personal_info_form"):
            st.markdown("**Basic Information**")
            
            col2a, col2b = st.columns(2)
            
            with col2a:
                first_name = st.text_input(
                    "First Name",
                    value=user_data.get('first_name', ''),
                    placeholder="Enter your first name"
                )
                
                email = st.text_input(
                    "Email Address",
                    value=user_data.get('email', ''),
                    placeholder="Enter your email",
                    disabled=True,  # Email changes require verification
                    help="Email changes require verification and admin approval"
                )
            
            with col2b:
                last_name = st.text_input(
                    "Last Name",
                    value=user_data.get('last_name', ''),
                    placeholder="Enter your last name"
                )
                
                username = st.text_input(
                    "Username",
                    value=user_data.get('username', ''),
                    placeholder="Choose a username (optional)"
                )
            
            # Additional fields
            full_name = st.text_input(
                "Display Name",
                value=user_data.get('full_name', ''),
                placeholder="How your name appears to others"
            )
            
            website = st.text_input(
                "Website",
                value=user_data.get('website', ''),
                placeholder="https://yourwebsite.com (optional)"
            )
            
            bio = st.text_area(
                "Bio",
                value=user_data.get('bio', ''),
                placeholder="Tell us about yourself (optional)",
                max_chars=500
            )
            
            # Submit button
            col2c, col2d, col2e = st.columns([1, 2, 1])
            with col2d:
                submit_personal = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            if submit_personal:
                # Validate inputs
                errors = []
                
                if not first_name or not last_name:
                    errors.append("First name and last name are required")
                
                if username and len(username) < 3:
                    errors.append("Username must be at least 3 characters long")
                
                if website and not website.startswith(('http://', 'https://')):
                    errors.append("Website must start with http:// or https://")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Update profile
                    update_data = {
                        'first_name': sanitize_input(first_name),
                        'last_name': sanitize_input(last_name),
                        'full_name': sanitize_input(full_name) or f"{first_name} {last_name}",
                        'username': sanitize_input(username) if username else None,
                        'website': sanitize_input(website) if website else None,
                        'bio': sanitize_input(bio) if bio else None,
                        'updated_at': st.session_state.get('current_time', '2024-01-01T00:00:00Z')
                    }
                    
                    if db.update_user_profile(user_id, update_data):
                        st.success("✅ Profile updated successfully!")
                        
                        # Log the action
                        log_user_action(user_id, "profile_update", "User updated personal information")
                        
                        # Update session state
                        st.session_state['user_data'].update(update_data)
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to update profile. Please try again.")

def show_security_section(user_data: Dict, auth_manager: AuthManager):
    """Show security settings section"""
    
    st.markdown("### 🔒 Security Settings")
    
    # Password change section
    st.markdown("#### Change Password")
    
    with st.form("password_change_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Enter new password"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Confirm new password"
            )
        
        # Password strength indicator
        if new_password:
            password_validation = validate_password(new_password)
            
            if password_validation['strength'] == 'strong':
                st.success("🔒 Strong password")
            elif password_validation['strength'] == 'medium':
                st.warning("🔐 Medium strength password")
            else:
                st.error("🔓 Weak password")
            
            if password_validation['errors']:
                for error in password_validation['errors']:
                    st.caption(f"• {error}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            change_password_btn = st.form_submit_button("🔒 Change Password", use_container_width=True)
        
        if change_password_btn:
            errors = []
            
            if not current_password:
                errors.append("Current password is required")
            
            if not new_password:
                errors.append("New password is required")
            
            if new_password != confirm_password:
                errors.append("New passwords do not match")
            
            password_validation = validate_password(new_password)
            if not password_validation['valid']:
                errors.extend(password_validation['errors'])
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # In a real implementation, you would verify the current password
                # and update it through Supabase Auth
                st.info("🔄 Password change functionality would be implemented here with Supabase Auth")
                
                # Log the action
                user_id = auth_manager.get_current_user_id()
                log_user_action(user_id, "password_change", "User changed password")
    
    st.markdown("---")
    
    # Two-factor authentication section
    st.markdown("#### 🛡️ Two-Factor Authentication")
    
    tfa_enabled = user_data.get('two_factor_enabled', False)
    
    if tfa_enabled:
        show_alert("Two-factor authentication is enabled for your account.", "success")
        
        if st.button("🔓 Disable Two-Factor Authentication"):
            if show_confirmation_dialog("Are you sure you want to disable two-factor authentication?", "disable_2fa"):
                st.info("Two-factor authentication disabled.")
                # Implementation would go here
    else:
        show_alert("Two-factor authentication is not enabled. Enable it for better security.", "warning")
        
        if st.button("🔒 Enable Two-Factor Authentication"):
            st.info("Two-factor authentication setup would be implemented here with QR codes and backup codes.")
    
    st.markdown("---")
    
    # Account security info
    st.markdown("#### 🔍 Account Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <strong>📅 Account Created</strong><br>
            <span style="color: #666;">{safe_date_format(user_data.get('created_at', ''), '%B %d, %Y')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <strong>🕐 Last Login</strong><br>
            <span style="color: #666;">{safe_date_format(user_data.get('last_sign_in_at', ''), '%B %d, %Y at %I:%M %p')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Email verification status
    email_verified = user_data.get('email_confirmed_at') is not None
    
    if email_verified:
        show_alert("✅ Your email address is verified.", "success")
    else:
        show_alert("⚠️ Your email address is not verified. Please check your email for verification instructions.", "warning")
        
        if st.button("📧 Resend Verification Email"):
            st.info("Verification email resent! Please check your inbox.")

def show_preferences_section(user_data: Dict, db: DatabaseManager, user_id: str):
    """Show user preferences section"""
    
    st.markdown("### ⚙️ Preferences")
    
    # Get current preferences
    current_prefs = db.get_user_preferences(user_id)
    
    with st.form("preferences_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎨 Appearance**")
            
            theme = st.selectbox(
                "Theme",
                options=["light", "dark", "auto"],
                index=["light", "dark", "auto"].index(current_prefs.get('theme', 'light')),
                help="Choose your preferred theme"
            )
            
            language = st.selectbox(
                "Language",
                options=["en", "es", "fr", "de", "it", "pt", "zh", "ja"],
                index=["en", "es", "fr", "de", "it", "pt", "zh", "ja"].index(current_prefs.get('language', 'en')),
                format_func=lambda x: {
                    'en': 'English',
                    'es': 'Español',
                    'fr': 'Français',
                    'de': 'Deutsch',
                    'it': 'Italiano',
                    'pt': 'Português',
                    'zh': '中文',
                    'ja': '日本語'
                }.get(x, x)
            )
            
            timezone = st.selectbox(
                "Timezone",
                options=["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo"],
                index=0,  # Default to UTC
                help="Your local timezone for date/time display"
            )
        
        with col2:
            st.markdown("**📢 Notifications**")
            
            email_notifications = st.checkbox(
                "Email Notifications",
                value=current_prefs.get('email_notifications', True),
                help="Receive important updates via email"
            )
            
            push_notifications = st.checkbox(
                "Push Notifications",
                value=current_prefs.get('push_notifications', True),
                help="Receive browser push notifications"
            )
            
            marketing_emails = st.checkbox(
                "Marketing Emails",
                value=current_prefs.get('marketing_emails', False),
                help="Receive promotional emails and newsletters"
            )
            
            weekly_digest = st.checkbox(
                "Weekly Digest",
                value=current_prefs.get('weekly_digest', True),
                help="Receive weekly summary of your activity"
            )
        
        st.markdown("**🔧 Advanced Settings**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            auto_save = st.checkbox(
                "Auto-save Drafts",
                value=current_prefs.get('auto_save', True),
                help="Automatically save your work as you type"
            )
            
            compact_mode = st.checkbox(
                "Compact Mode",
                value=current_prefs.get('compact_mode', False),
                help="Use a more compact interface layout"
            )
        
        with col4:
            analytics_tracking = st.checkbox(
                "Analytics Tracking",
                value=current_prefs.get('analytics_tracking', True),
                help="Help us improve by sharing anonymous usage data"
            )
            
            beta_features = st.checkbox(
                "Beta Features",
                value=current_prefs.get('beta_features', False),
                help="Get early access to new features (may be unstable)"
            )
        
        # Submit button
        col5, col6, col7 = st.columns([1, 2, 1])
        with col6:
            save_preferences = st.form_submit_button("💾 Save Preferences", use_container_width=True)
        
        if save_preferences:
            new_preferences = {
                'theme': theme,
                'language': language,
                'timezone': timezone,
                'email_notifications': email_notifications,
                'push_notifications': push_notifications,
                'marketing_emails': marketing_emails,
                'weekly_digest': weekly_digest,
                'auto_save': auto_save,
                'compact_mode': compact_mode,
                'analytics_tracking': analytics_tracking,
                'beta_features': beta_features,
                'updated_at': st.session_state.get('current_time', '2024-01-01T00:00:00Z')
            }
            
            if db.update_user_preferences(user_id, new_preferences):
                st.success("✅ Preferences saved successfully!")
                
                # Log the action
                log_user_action(user_id, "preferences_update", "User updated preferences")
                
                st.rerun()
            else:
                st.error("❌ Failed to save preferences. Please try again.")

def show_account_details_section(user_data: Dict):
    """Show account details and subscription information"""
    
    st.markdown("### 📊 Account Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💳 Subscription Information")
        
        subscription_tier = user_data.get('subscription_tier', 'free').title()
        subscription_status = user_data.get('subscription_status', 'active').title()
        
        st.markdown(f"""
        <div class="feature-card">
            <strong>Current Plan:</strong> {subscription_tier}<br>
            <strong>Status:</strong> {subscription_status}<br>
            <strong>Billing Cycle:</strong> Monthly<br>
            <strong>Next Billing:</strong> {safe_date_format(user_data.get('subscription_end_date', ''), '%B %d, %Y')}
        </div>
        """, unsafe_allow_html=True)
        
        if user_data.get('subscription_tier') == 'free':
            st.markdown("#### 🌟 Upgrade Benefits")
            st.markdown("""
            <div class="feature-card" style="border-left-color: #ffc107;">
                <strong>Pro Plan Benefits:</strong><br>
                • 100,000 tokens/month<br>
                • 50 file uploads<br>
                • 100 chat threads<br>
                • Priority support<br>
                • Advanced features<br>
                • Custom assistants
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⬆️ Upgrade to Pro", use_container_width=True):
                st.info("Upgrade functionality would redirect to billing page")
    
    with col2:
        st.markdown("#### 📈 Usage Statistics")
        
        st.markdown(f"""
        <div class="feature-card">
            <strong>Tokens Used This Month:</strong> {user_data.get('tokens_used', 0):,}<br>
            <strong>Total API Requests:</strong> {user_data.get('api_requests', 0):,}<br>
            <strong>Chat Threads:</strong> {user_data.get('chat_threads_count', 0)}<br>
            <strong>File Uploads:</strong> {user_data.get('file_uploads_count', 0)}<br>
            <strong>Custom Assistants:</strong> {user_data.get('custom_assistants_count', 0)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🔗 Account Actions")
        
        col2a, col2b = st.columns(2)
        
        with col2a:
            if st.button("📥 Export Data", use_container_width=True):
                st.info("Data export functionality would generate a downloadable file with all your data")
        
        with col2b:
            if st.button("🗑️ Delete Account", use_container_width=True, type="secondary"):
                if show_confirmation_dialog("Are you sure you want to delete your account? This action cannot be undone.", "delete_account"):
                    st.error("Account deletion would be processed here")
    
    # Account ID and technical details
    st.markdown("---")
    st.markdown("#### 🔧 Technical Details")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <strong>Account ID:</strong> {user_data.get('id', 'N/A')}<br>
            <strong>Email Verified:</strong> {'Yes' if user_data.get('email_confirmed_at') else 'No'}<br>
            <strong>Account Created:</strong> {safe_date_format(user_data.get('created_at', ''), '%B %d, %Y')}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="feature-card">
            <strong>Last Login:</strong> {safe_date_format(user_data.get('last_sign_in_at', ''), '%B %d, %Y')}<br>
            <strong>Profile Updated:</strong> {safe_date_format(user_data.get('updated_at', ''), '%B %d, %Y')}<br>
            <strong>Role:</strong> {user_data.get('role', 'user').title()}
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
