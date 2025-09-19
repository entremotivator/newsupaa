import streamlit as st
import os
from components.auth import AuthManager
from components.database import init_service_client
from components.ui_components import load_custom_css

# Page configuration
st.set_page_config(
    page_title="User Management System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point with authentication"""
    
    # Load custom styling
    load_custom_css()
    
    # Initialize authentication manager
    auth_manager = AuthManager()
    
    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        show_auth_page(auth_manager)
    else:
        show_main_app()

def show_auth_page(auth_manager):
    """Display authentication page with login/signup options"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2e7d32; font-size: 3rem; margin-bottom: 0.5rem;">🔐</h1>
        <h2 style="color: #2e7d32; margin-bottom: 2rem;">User Management System</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        show_login_form(auth_manager)
    
    with tab2:
        show_signup_form(auth_manager)

def show_login_form(auth_manager):
    """Display login form"""
    
    st.markdown("### Welcome Back!")
    st.markdown("Please enter your credentials to access the system.")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button("🔑 Login", use_container_width=True)
        
        if login_button:
            if email and password:
                success, user_data, message = auth_manager.login(email, password)
                
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['user_data'] = user_data
                    st.session_state['user_role'] = user_data.get('role', 'user')
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all fields")

def show_signup_form(auth_manager):
    """Display signup form"""
    
    st.markdown("### Create New Account")
    st.markdown("Join our platform by creating a new account.")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("👤 First Name", placeholder="Enter your first name")
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            
        with col2:
            last_name = st.text_input("👤 Last Name", placeholder="Enter your last name")
            password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            signup_button = st.form_submit_button("📝 Create Account", use_container_width=True)
        
        if signup_button:
            if all([first_name, last_name, email, password, confirm_password]):
                if password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                elif not terms_accepted:
                    st.error("❌ Please accept the Terms of Service and Privacy Policy")
                else:
                    success, message = auth_manager.signup(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.info("📧 Please check your email to verify your account before logging in.")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all fields")

def show_main_app():
    """Display main application interface based on user role"""
    
    user_data = st.session_state.get('user_data', {})
    user_role = st.session_state.get('user_role', 'user')
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #c8e6c9 0%, #ffffff 100%); border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: #2e7d32; margin: 0;">Welcome!</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">{user_data.get('email', 'User')}</p>
            <small style="color: #888;">Role: {user_role.title()}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation based on role
        if user_role == 'admin':
            st.markdown("### 🔧 Admin Navigation")
            st.page_link("pages/01_🏠_User_Dashboard.py", label="🏠 Dashboard")
            st.page_link("pages/02_👤_Profile_Settings.py", label="👤 Profile")
            st.page_link("pages/03_📊_Usage_Analytics.py", label="📊 Analytics")
            st.page_link("pages/04_🔧_Admin_Panel.py", label="🔧 Admin Panel")
            st.page_link("pages/05_👥_User_Management.py", label="👥 User Management")
        else:
            st.markdown("### 🏠 User Navigation")
            st.page_link("pages/01_🏠_User_Dashboard.py", label="🏠 Dashboard")
            st.page_link("pages/02_👤_Profile_Settings.py", label="👤 Profile")
            st.page_link("pages/03_📊_Usage_Analytics.py", label="📊 My Analytics")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2e7d32;">🏠 Welcome to Your Dashboard</h1>
        <p style="color: #666; font-size: 1.2rem;">Select a page from the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats for the main page
    show_quick_stats(user_data, user_role)

def show_quick_stats(user_data, user_role):
    """Display quick statistics on the main page"""
    
    if user_role == 'admin':
        st.markdown("### 📊 System Overview")
        
        # Initialize database client
        try:
            supabase = init_service_client()
            
            # Get basic stats
            users_response = supabase.table("profiles").select("id").execute()
            total_users = len(users_response.data) if users_response.data else 0
            
            pending_response = supabase.table("pending_signups").select("id").eq("status", "pending").execute()
            pending_approvals = len(pending_response.data) if pending_response.data else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="metric-value">{total_users}</div>
                    <div class="metric-label">Total Users</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="metric-value">{pending_approvals}</div>
                    <div class="metric-label">Pending Approvals</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="metric-value">Active</div>
                    <div class="metric-label">System Status</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="metric-value">Online</div>
                    <div class="metric-label">Database</div>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading system stats: {str(e)}")
    
    else:
        st.markdown("### 👤 Your Account")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="metric-value">Active</div>
                <div class="metric-label">Account Status</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="metric-value">Free</div>
                <div class="metric-label">Subscription</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Usage This Month</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
