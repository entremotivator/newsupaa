import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

def load_custom_css():
    """Load custom CSS styling for the application"""
    st.markdown("""
    <style>
    /* Main theme colors - Light Green */
    .main {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    /* Card styling */
    .user-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #4caf50;
        transition: transform 0.2s ease;
    }
    
    .user-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .admin-card {
        border-left-color: #ff9800;
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    }
    
    .moderator-card {
        border-left-color: #9c27b0;
        background: linear-gradient(135deg, #f3e5f5 0%, #ffffff 100%);
    }
    
    .pending-card {
        border-left-color: #f44336;
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    }
    
    .premium-card {
        border-left-color: #ffc107;
        background: linear-gradient(135deg, #fffde7 0%, #ffffff 100%);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #c8e6c9 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #a5d6a7;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
        transform: translateY(-1px);
    }
    
    /* Approval buttons */
    .approve-btn {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%) !important;
    }
    
    .reject-btn {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%) !important;
    }
    
    .warning-btn {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #c8e6c9 0%, #e8f5e8 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
        border-left: 4px solid #f44336;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
        border-left: 4px solid #ff9800;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #c8e6c9;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #c8e6c9;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #c8e6c9;
    }
    
    /* Activity indicators */
    .activity-high { color: #4caf50; font-weight: bold; }
    .activity-medium { color: #ff9800; font-weight: bold; }
    .activity-low { color: #f44336; font-weight: bold; }
    
    /* Profile card styling */
    .profile-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /* Progress bars */
    .progress-container {
        background: #f0f0f0;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4caf50 0%, #66bb6a 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Alert styling */
    .alert {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
        border-left-color: #ff9800;
        color: #f57c00;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
        border-left-color: #f44336;
        color: #d32f2f;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
        border-left-color: #2196f3;
        color: #1976d2;
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #4caf50;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .stats-card {
            padding: 15px;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .user-card, .dashboard-card {
            padding: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_loading_spinner(text: str = "Loading..."):
    """Display a loading spinner with text"""
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <div class="loading-spinner"></div>
        <p style="color: #666; margin-top: 10px;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

def show_alert(message: str, alert_type: str = "info"):
    """Display a styled alert message"""
    alert_class = f"alert alert-{alert_type}"
    icon_map = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    icon = icon_map.get(alert_type, "ℹ️")
    
    st.markdown(f"""
    <div class="{alert_class}">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title: str, value: str, subtitle: str = "", color: str = "#2e7d32"):
    """Create a metric card component"""
    st.markdown(f"""
    <div class="stats-card">
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{title}</div>
        {f'<small style="color: #888;">{subtitle}</small>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(percentage: float, label: str = "", color: str = "#4caf50"):
    """Create a progress bar component"""
    st.markdown(f"""
    <div>
        {f'<p style="margin-bottom: 5px; color: #666;">{label}</p>' if label else ''}
        <div class="progress-container">
            <div class="progress-bar" style="width: {percentage}%; background: linear-gradient(90deg, {color} 0%, {color}aa 100%);"></div>
        </div>
        <small style="color: #888;">{percentage:.1f}%</small>
    </div>
    """, unsafe_allow_html=True)

def safe_date_format(date_string: str, format_str: str = '%Y-%m-%d') -> str:
    """Safely format date strings with error handling"""
    if not date_string:
        return "Not set"
    
    try:
        # Handle different date formats
        if 'T' in date_string:
            # ISO format with time
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_string)
        else:
            # Simple date format
            dt = datetime.strptime(date_string, '%Y-%m-%d')
        
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return "Invalid date"

def calculate_activity_score(last_sign_in: str) -> str:
    """Calculate user activity score based on last sign in"""
    if not last_sign_in:
        return "Never"
    
    try:
        if 'T' in last_sign_in:
            if last_sign_in.endswith('Z'):
                last_sign_in = last_sign_in.replace('Z', '+00:00')
            last_login = datetime.fromisoformat(last_sign_in)
        else:
            last_login = datetime.strptime(last_sign_in, '%Y-%m-%d')
        
        now = datetime.now(last_login.tzinfo) if last_login.tzinfo else datetime.now()
        days_ago = (now - last_login).days
        
        if days_ago == 0:
            return "Today"
        elif days_ago == 1:
            return "Yesterday"
        elif days_ago <= 7:
            return f"{days_ago} days ago"
        elif days_ago <= 30:
            return f"{days_ago // 7} weeks ago"
        elif days_ago <= 365:
            return f"{days_ago // 30} months ago"
        else:
            return f"{days_ago // 365} years ago"
    except:
        return "Unknown"

def get_activity_class(activity_score: str) -> str:
    """Get CSS class for activity level"""
    if activity_score in ["Today", "Yesterday"]:
        return "activity-high"
    elif "days ago" in activity_score or "weeks ago" in activity_score:
        return "activity-medium"
    else:
        return "activity-low"

def create_user_card(user: Dict, card_type: str = "default"):
    """Create a user card component"""
    
    # Determine card class based on user role and type
    card_classes = ["user-card"]
    
    if user.get('role') == 'admin':
        card_classes.append("admin-card")
    elif user.get('role') == 'moderator':
        card_classes.append("moderator-card")
    elif user.get('pending_approval', False):
        card_classes.append("pending-card")
    elif user.get('subscription_tier') in ['pro', 'enterprise']:
        card_classes.append("premium-card")
    
    card_class = " ".join(card_classes)
    
    # Format dates
    created_date = safe_date_format(user.get('created_at', ''), '%Y-%m-%d')
    last_login = safe_date_format(user.get('last_sign_in_at', ''), '%Y-%m-%d %H:%M')
    
    # Activity score and class
    activity_score = calculate_activity_score(user.get('last_sign_in_at', ''))
    activity_class = get_activity_class(activity_score)
    
    # Role badge color
    role_colors = {
        'admin': '#ff9800',
        'moderator': '#9c27b0',
        'user': '#4caf50'
    }
    role_color = role_colors.get(user.get('role', 'user'), '#4caf50')
    
    st.markdown(f"""
    <div class="{card_class}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
            <div>
                <h4 style="margin: 0; color: #333;">{user.get('full_name', 'Unnamed User')}</h4>
                <p style="margin: 5px 0; color: #666;">{user.get('email', 'No email')}</p>
                <span style="background: {role_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">
                    {user.get('role', 'user').title()}
                </span>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; color: #888; font-size: 0.9rem;">ID: {user.get('id', 'N/A')[:8]}...</p>
                <p style="margin: 5px 0 0 0; color: #888; font-size: 0.9rem;">Created: {created_date}</p>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
            <div>
                <p style="margin: 0; color: #666; font-size: 0.9rem;"><strong>Subscription:</strong> {user.get('subscription_tier', 'free').title()}</p>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;"><strong>Status:</strong> {'Active' if user.get('is_active', True) else 'Inactive'}</p>
            </div>
            <div>
                <p style="margin: 0; color: #666; font-size: 0.9rem;"><strong>Last Login:</strong> <span class="{activity_class}">{activity_score}</span></p>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;"><strong>Tokens Used:</strong> {user.get('tokens_used', 0):,}</p>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; gap: 10px;">
                <small style="color: #888;">Threads: {user.get('chat_threads_count', 0)}</small>
                <small style="color: #888;">Files: {user.get('file_uploads_count', 0)}</small>
                <small style="color: #888;">Assistants: {user.get('custom_assistants_count', 0)}</small>
            </div>
            <div>
                <small style="color: #888;">Cost: ${user.get('total_cost', 0):.2f}</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_dashboard_card(title: str, content: str, icon: str = "📊"):
    """Create a dashboard card component"""
    st.markdown(f"""
    <div class="dashboard-card">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <span style="font-size: 1.5rem; margin-right: 10px;">{icon}</span>
            <h3 style="margin: 0; color: #333;">{title}</h3>
        </div>
        <div>
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_confirmation_dialog(message: str, key: str) -> bool:
    """Show a confirmation dialog and return True if confirmed"""
    if f"confirm_{key}" not in st.session_state:
        st.session_state[f"confirm_{key}"] = False
    
    if not st.session_state[f"confirm_{key}"]:
        st.warning(f"⚠️ {message}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm", key=f"confirm_yes_{key}"):
                st.session_state[f"confirm_{key}"] = True
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key=f"confirm_no_{key}"):
                return False
        return False
    else:
        # Reset confirmation state
        st.session_state[f"confirm_{key}"] = False
        return True

def format_number(number: float, format_type: str = "default") -> str:
    """Format numbers for display"""
    if format_type == "currency":
        return f"${number:.2f}"
    elif format_type == "percentage":
        return f"{number:.1f}%"
    elif format_type == "compact":
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(int(number))
    else:
        return f"{number:,.0f}" if number >= 1000 else str(int(number))
