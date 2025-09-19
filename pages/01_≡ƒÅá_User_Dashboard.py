import streamlit as st
import sys
import os

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.auth import AuthManager
from components.database import DatabaseManager
from components.ui_components import (
    load_custom_css, create_metric_card, create_progress_bar, 
    create_dashboard_card, show_alert, time_ago
)
from components.utils import (
    calculate_usage_percentage, get_subscription_limits, 
    format_currency, calculate_user_score
)
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="User Dashboard",
    page_icon="🏠",
    layout="wide"
)

def main():
    """Main dashboard page"""
    
    # Load custom styling
    load_custom_css()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Require authentication
    auth_manager.require_auth()
    
    # Get current user data
    user_data = st.session_state.get('user_data', {})
    user_id = auth_manager.get_current_user_id()
    user_role = auth_manager.get_current_user_role()
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Page header
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="color: #2e7d32; margin-bottom: 0.5rem;">🏠 Welcome, {user_data.get('full_name', 'User')}!</h1>
        <p style="color: #666; font-size: 1.1rem;">Here's your personalized dashboard overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user statistics
    usage_stats = db.get_user_usage_stats(user_id) if user_id else {}
    user_preferences = db.get_user_preferences(user_id) if user_id else {}
    recent_activities = db.get_user_activity_logs(user_id, limit=10) if user_id else []
    
    # Main dashboard content
    show_dashboard_overview(user_data, usage_stats, user_preferences)
    
    st.markdown("---")
    
    # Dashboard sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_usage_analytics(user_data, usage_stats)
        show_recent_activity(recent_activities)
    
    with col2:
        show_quick_stats(user_data, usage_stats)
        show_account_info(user_data)

def show_dashboard_overview(user_data: Dict, usage_stats: Dict, preferences: Dict):
    """Show main dashboard overview with key metrics"""
    
    # Get subscription limits
    subscription_tier = user_data.get('subscription_tier', 'free')
    limits = get_subscription_limits(subscription_tier)
    
    # Calculate usage percentages
    token_usage = calculate_usage_percentage(
        usage_stats.get('total_tokens', 0), 
        limits['monthly_tokens']
    )
    
    file_usage = calculate_usage_percentage(
        usage_stats.get('file_uploads_count', 0), 
        limits['max_files']
    )
    
    thread_usage = calculate_usage_percentage(
        usage_stats.get('chat_threads_count', 0), 
        limits['max_threads']
    )
    
    # Main metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card(
            "Account Status",
            "Active" if user_data.get('is_active', True) else "Inactive",
            f"{subscription_tier.title()} Plan",
            "#4caf50" if user_data.get('is_active', True) else "#f44336"
        )
    
    with col2:
        create_metric_card(
            "Tokens Used",
            f"{usage_stats.get('total_tokens', 0):,}",
            f"of {limits['monthly_tokens']:,}",
            "#4caf50" if token_usage < 80 else "#ff9800" if token_usage < 95 else "#f44336"
        )
    
    with col3:
        create_metric_card(
            "Total Cost",
            format_currency(usage_stats.get('total_cost', 0)),
            "This month",
            "#2e7d32"
        )
    
    with col4:
        create_metric_card(
            "Chat Threads",
            str(usage_stats.get('chat_threads_count', 0)),
            f"of {limits['max_threads']} max",
            "#4caf50" if thread_usage < 80 else "#ff9800"
        )
    
    with col5:
        user_score = calculate_user_score(user_data)
        create_metric_card(
            "Engagement Score",
            f"{user_score}/100",
            "Based on activity",
            "#4caf50" if user_score > 70 else "#ff9800" if user_score > 40 else "#f44336"
        )
    
    # Usage progress bars
    st.markdown("### 📊 Usage Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_progress_bar(
            token_usage,
            f"Token Usage ({usage_stats.get('total_tokens', 0):,} / {limits['monthly_tokens']:,})",
            "#4caf50" if token_usage < 80 else "#ff9800" if token_usage < 95 else "#f44336"
        )
    
    with col2:
        create_progress_bar(
            file_usage,
            f"File Storage ({usage_stats.get('file_uploads_count', 0)} / {limits['max_files']})",
            "#4caf50" if file_usage < 80 else "#ff9800"
        )
    
    with col3:
        create_progress_bar(
            thread_usage,
            f"Chat Threads ({usage_stats.get('chat_threads_count', 0)} / {limits['max_threads']})",
            "#4caf50" if thread_usage < 80 else "#ff9800"
        )

def show_usage_analytics(user_data: Dict, usage_stats: Dict):
    """Show usage analytics charts"""
    
    st.markdown("### 📈 Usage Analytics")
    
    # Create sample data for demonstration (in real app, this would come from database)
    # Token usage over time
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
    token_usage_daily = [max(0, usage_stats.get('total_tokens', 0) // 30 + (i % 7) * 100) for i in range(30)]
    
    # Create charts in tabs
    tab1, tab2, tab3 = st.tabs(["📊 Token Usage", "💰 Cost Analysis", "🔄 Activity Trends"])
    
    with tab1:
        fig_tokens = px.line(
            x=dates,
            y=token_usage_daily,
            title="Daily Token Usage (Last 30 Days)",
            labels={'x': 'Date', 'y': 'Tokens Used'}
        )
        fig_tokens.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        fig_tokens.update_traces(line_color='#4caf50')
        st.plotly_chart(fig_tokens, use_container_width=True)
    
    with tab2:
        # Cost breakdown pie chart
        cost_data = {
            'API Calls': usage_stats.get('total_cost', 0) * 0.7,
            'Storage': usage_stats.get('total_cost', 0) * 0.2,
            'Features': usage_stats.get('total_cost', 0) * 0.1
        }
        
        if sum(cost_data.values()) > 0:
            fig_cost = px.pie(
                values=list(cost_data.values()),
                names=list(cost_data.keys()),
                title="Cost Breakdown This Month"
            )
            fig_cost.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("No cost data available yet. Start using the platform to see your cost breakdown!")
    
    with tab3:
        # Activity types bar chart
        activity_types = {
            'Chat Sessions': usage_stats.get('chat_threads_count', 0),
            'File Uploads': usage_stats.get('file_uploads_count', 0),
            'Custom Assistants': usage_stats.get('custom_assistants_count', 0),
            'API Requests': usage_stats.get('total_requests', 0)
        }
        
        fig_activity = px.bar(
            x=list(activity_types.keys()),
            y=list(activity_types.values()),
            title="Activity Summary",
            color=list(activity_types.values()),
            color_continuous_scale='Greens'
        )
        fig_activity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            xaxis_title="Activity Type",
            yaxis_title="Count"
        )
        st.plotly_chart(fig_activity, use_container_width=True)

def show_recent_activity(activities: List[Dict]):
    """Show recent user activities"""
    
    st.markdown("### 📋 Recent Activity")
    
    if activities:
        for activity in activities[:5]:  # Show last 5 activities
            activity_time = time_ago(activity.get('created_at', ''))
            activity_type = activity.get('activity_type', 'Unknown').title()
            description = activity.get('description', 'No description')
            
            st.markdown(f"""
            <div class="dashboard-card" style="margin: 10px 0; padding: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #2e7d32;">{activity_type}</strong>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;">{description}</p>
                    </div>
                    <small style="color: #888;">{activity_time}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(activities) > 5:
            st.info(f"Showing 5 of {len(activities)} recent activities. View all in your profile.")
    else:
        st.info("No recent activity found. Start using the platform to see your activity here!")

def show_quick_stats(user_data: Dict, usage_stats: Dict):
    """Show quick statistics sidebar"""
    
    st.markdown("### ⚡ Quick Stats")
    
    # Account age
    created_date = user_data.get('created_at', '')
    if created_date:
        account_age = time_ago(created_date)
        st.markdown(f"""
        <div class="feature-card">
            <strong>👤 Account Age</strong><br>
            <span style="color: #666;">{account_age}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Last login
    last_login = user_data.get('last_sign_in_at', '')
    if last_login:
        last_login_ago = time_ago(last_login)
        st.markdown(f"""
        <div class="feature-card">
            <strong>🕐 Last Login</strong><br>
            <span style="color: #666;">{last_login_ago}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature usage
    st.markdown(f"""
    <div class="feature-card">
        <strong>🎯 Feature Usage</strong><br>
        <small style="color: #666;">
            • Chat Threads: {usage_stats.get('chat_threads_count', 0)}<br>
            • File Uploads: {usage_stats.get('file_uploads_count', 0)}<br>
            • Custom Assistants: {usage_stats.get('custom_assistants_count', 0)}<br>
            • API Requests: {usage_stats.get('total_requests', 0)}
        </small>
    </div>
    """, unsafe_allow_html=True)

def show_account_info(user_data: Dict):
    """Show account information"""
    
    st.markdown("### ℹ️ Account Info")
    
    subscription_tier = user_data.get('subscription_tier', 'free').title()
    subscription_status = user_data.get('subscription_status', 'active').title()
    
    st.markdown(f"""
    <div class="feature-card">
        <strong>💳 Subscription</strong><br>
        <span style="color: #666;">{subscription_tier} Plan</span><br>
        <small style="color: #888;">Status: {subscription_status}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Account features
    features = []
    if user_data.get('voice_enabled'):
        features.append("🎤 Voice Features")
    if user_data.get('advanced_features'):
        features.append("⚡ Advanced Features")
    
    if features:
        st.markdown(f"""
        <div class="feature-card">
            <strong>🚀 Enabled Features</strong><br>
            <small style="color: #666;">
                {'<br>'.join(features)}
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### 🔧 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Edit Profile", use_container_width=True):
            st.switch_page("pages/02_👤_Profile_Settings.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/03_📊_Usage_Analytics.py")
    
    # Upgrade prompt for free users
    if user_data.get('subscription_tier') == 'free':
        st.markdown("### 🌟 Upgrade Your Plan")
        st.markdown("""
        <div class="feature-card" style="border-left-color: #ffc107;">
            <strong>Unlock More Features!</strong><br>
            <small style="color: #666;">
                • 10x more tokens<br>
                • Advanced features<br>
                • Priority support<br>
                • Custom assistants
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⬆️ Upgrade Now", use_container_width=True):
            st.info("Upgrade functionality would be implemented here!")

if __name__ == "__main__":
    main()
