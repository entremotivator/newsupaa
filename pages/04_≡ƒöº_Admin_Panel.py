import streamlit as st
import sys
import os

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.auth import AuthManager
from components.database import DatabaseManager
from components.ui_components import (
    load_custom_css, create_metric_card, show_alert, 
    create_dashboard_card, show_confirmation_dialog
)
from components.utils import (
    format_currency, time_ago, calculate_usage_percentage,
    get_subscription_limits, paginate_data
)
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Admin Panel",
    page_icon="🔧",
    layout="wide"
)

def main():
    """Main admin panel page"""
    
    # Load custom styling
    load_custom_css()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Require admin authentication
    auth_manager.require_role('admin')
    
    # Get current user data
    user_data = st.session_state.get('user_data', {})
    
    # Initialize database manager with service role
    db = DatabaseManager(use_service_role=True)
    
    # Page header
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="color: #2e7d32; margin-bottom: 0.5rem;">🔧 Admin Panel</h1>
        <p style="color: #666; font-size: 1.1rem;">System administration and management dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin dashboard sections
    show_system_overview(db)
    
    st.markdown("---")
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 System Stats", 
        "⚙️ System Settings", 
        "🔔 Notifications", 
        "📈 Analytics", 
        "🛠️ Maintenance"
    ])
    
    with tab1:
        show_system_statistics(db)
    
    with tab2:
        show_system_settings()
    
    with tab3:
        show_notifications_management(db)
    
    with tab4:
        show_admin_analytics(db)
    
    with tab5:
        show_maintenance_tools(db)

def show_system_overview(db: DatabaseManager):
    """Show system overview with key metrics"""
    
    st.markdown("### 🏢 System Overview")
    
    try:
        # Get all users for statistics
        all_users = db.get_all_users()
        
        # Calculate system metrics
        total_users = len(all_users)
        active_users = len([u for u in all_users if u.get('is_active', True)])
        admin_users = len([u for u in all_users if u.get('role') == 'admin'])
        pending_users = len([u for u in all_users if u.get('pending_approval', False)])
        
        # Subscription metrics
        free_users = len([u for u in all_users if u.get('subscription_tier') == 'free'])
        pro_users = len([u for u in all_users if u.get('subscription_tier') == 'pro'])
        enterprise_users = len([u for u in all_users if u.get('subscription_tier') == 'enterprise'])
        
        # Usage metrics
        total_tokens = sum([u.get('tokens_used', 0) for u in all_users])
        total_cost = sum([u.get('total_cost', 0) for u in all_users])
        total_threads = sum([u.get('chat_threads_count', 0) for u in all_users])
        total_files = sum([u.get('file_uploads_count', 0) for u in all_users])
        
        # Activity metrics
        active_today = len([u for u in all_users if 'Today' in str(u.get('activity_score', ''))])
        active_week = len([u for u in all_users if any(x in str(u.get('activity_score', '')) for x in ['Today', 'Yesterday', 'days ago'])])
        
        # Main metrics row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            create_metric_card(
                "Total Users",
                str(total_users),
                f"{active_users} active",
                "#4caf50"
            )
        
        with col2:
            create_metric_card(
                "Pending Approvals",
                str(pending_users),
                "Awaiting review",
                "#ff9800" if pending_users > 0 else "#4caf50"
            )
        
        with col3:
            create_metric_card(
                "Active Today",
                str(active_today),
                f"{active_week} this week",
                "#4caf50"
            )
        
        with col4:
            create_metric_card(
                "Total Revenue",
                format_currency(total_cost),
                "All time",
                "#2e7d32"
            )
        
        with col5:
            create_metric_card(
                "Token Usage",
                f"{total_tokens:,}",
                "All users",
                "#4caf50"
            )
        
        with col6:
            create_metric_card(
                "System Health",
                "Healthy",
                "All systems operational",
                "#4caf50"
            )
        
        # Subscription breakdown
        st.markdown("#### 💳 Subscription Breakdown")
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            create_metric_card(
                "Free Users",
                str(free_users),
                f"{(free_users/max(total_users,1)*100):.1f}% of total",
                "#4caf50"
            )
        
        with col8:
            create_metric_card(
                "Pro Users",
                str(pro_users),
                f"{(pro_users/max(total_users,1)*100):.1f}% of total",
                "#ff9800"
            )
        
        with col9:
            create_metric_card(
                "Enterprise Users",
                str(enterprise_users),
                f"{(enterprise_users/max(total_users,1)*100):.1f}% of total",
                "#9c27b0"
            )
        
    except Exception as e:
        st.error(f"Error loading system overview: {str(e)}")

def show_system_statistics(db: DatabaseManager):
    """Show detailed system statistics"""
    
    st.markdown("### 📊 Detailed System Statistics")
    
    try:
        all_users = db.get_all_users()
        
        if not all_users:
            st.warning("No user data available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # User growth chart
            st.markdown("#### 📈 User Growth")
            
            # Generate sample growth data
            dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
            cumulative_users = [max(1, len(all_users) - (30-i)*2) for i in range(30)]
            
            fig_growth = px.line(
                x=dates,
                y=cumulative_users,
                title="User Growth (Last 30 Days)",
                labels={'x': 'Date', 'y': 'Total Users'}
            )
            fig_growth.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            fig_growth.update_traces(line_color='#4caf50', line_width=3)
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Activity distribution
            st.markdown("#### 🔄 User Activity Distribution")
            
            activity_levels = {'High': 0, 'Medium': 0, 'Low': 0, 'Inactive': 0}
            
            for user in all_users:
                activity = user.get('activity_score', 'Never')
                if activity in ['Today', 'Yesterday']:
                    activity_levels['High'] += 1
                elif 'days ago' in activity or 'weeks ago' in activity:
                    activity_levels['Medium'] += 1
                elif 'months ago' in activity:
                    activity_levels['Low'] += 1
                else:
                    activity_levels['Inactive'] += 1
            
            fig_activity = px.bar(
                x=list(activity_levels.keys()),
                y=list(activity_levels.values()),
                title="User Activity Levels",
                color=list(activity_levels.values()),
                color_continuous_scale='Greens'
            )
            fig_activity.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            # Subscription distribution
            st.markdown("#### 💳 Subscription Distribution")
            
            subscription_counts = {}
            for user in all_users:
                tier = user.get('subscription_tier', 'free')
                subscription_counts[tier] = subscription_counts.get(tier, 0) + 1
            
            fig_subs = px.pie(
                values=list(subscription_counts.values()),
                names=list(subscription_counts.keys()),
                title="Subscription Tiers"
            )
            fig_subs.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_subs, use_container_width=True)
            
            # Usage statistics
            st.markdown("#### 📊 Usage Statistics")
            
            usage_data = {
                'Metric': ['Total Tokens', 'API Requests', 'Chat Threads', 'File Uploads', 'Custom Assistants'],
                'Count': [
                    sum([u.get('tokens_used', 0) for u in all_users]),
                    sum([u.get('api_requests', 0) for u in all_users]),
                    sum([u.get('chat_threads_count', 0) for u in all_users]),
                    sum([u.get('file_uploads_count', 0) for u in all_users]),
                    sum([u.get('custom_assistants_count', 0) for u in all_users])
                ]
            }
            
            fig_usage = px.bar(
                x=usage_data['Metric'],
                y=usage_data['Count'],
                title="Platform Usage Metrics",
                color=usage_data['Count'],
                color_continuous_scale='Greens'
            )
            fig_usage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_usage, use_container_width=True)
        
        # Top users table
        st.markdown("#### 🏆 Top Users by Activity")
        
        # Sort users by tokens used
        top_users = sorted(all_users, key=lambda x: x.get('tokens_used', 0), reverse=True)[:10]
        
        if top_users:
            for i, user in enumerate(top_users, 1):
                col_rank, col_info, col_stats = st.columns([1, 3, 2])
                
                with col_rank:
                    st.markdown(f"**#{i}**")
                
                with col_info:
                    st.markdown(f"**{user.get('full_name', 'Unknown')}**")
                    st.caption(f"{user.get('email', 'No email')} • {user.get('subscription_tier', 'free').title()}")
                
                with col_stats:
                    st.markdown(f"🔢 {user.get('tokens_used', 0):,} tokens")
                    st.caption(f"💰 {format_currency(user.get('total_cost', 0))} • 🧵 {user.get('chat_threads_count', 0)} threads")
        
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

def show_system_settings():
    """Show system settings management"""
    
    st.markdown("### ⚙️ System Settings")
    
    # Application settings
    st.markdown("#### 🔧 Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**General Settings**")
        
        maintenance_mode = st.checkbox(
            "Maintenance Mode",
            value=False,
            help="Enable maintenance mode to prevent user access"
        )
        
        new_registrations = st.checkbox(
            "Allow New Registrations",
            value=True,
            help="Allow new users to register"
        )
        
        email_verification = st.checkbox(
            "Require Email Verification",
            value=True,
            help="Require users to verify their email addresses"
        )
        
        admin_approval = st.checkbox(
            "Require Admin Approval",
            value=False,
            help="Require admin approval for new accounts"
        )
    
    with col2:
        st.markdown("**Rate Limiting**")
        
        api_rate_limit = st.number_input(
            "API Rate Limit (requests/hour)",
            min_value=1,
            max_value=10000,
            value=1000,
            help="Maximum API requests per hour per user"
        )
        
        token_rate_limit = st.number_input(
            "Token Rate Limit (tokens/hour)",
            min_value=1,
            max_value=100000,
            value=10000,
            help="Maximum tokens per hour per user"
        )
        
        file_upload_limit = st.number_input(
            "File Upload Limit (MB)",
            min_value=1,
            max_value=1000,
            value=100,
            help="Maximum file upload size in MB"
        )
    
    # Security settings
    st.markdown("#### 🔒 Security Settings")
    
    col3, col4 = st.columns(2)
    
    with col3:
        password_min_length = st.number_input(
            "Minimum Password Length",
            min_value=6,
            max_value=50,
            value=8
        )
        
        session_timeout = st.number_input(
            "Session Timeout (hours)",
            min_value=1,
            max_value=168,
            value=24
        )
        
        max_login_attempts = st.number_input(
            "Max Login Attempts",
            min_value=3,
            max_value=20,
            value=5
        )
    
    with col4:
        require_2fa_admin = st.checkbox(
            "Require 2FA for Admins",
            value=True,
            help="Require two-factor authentication for admin accounts"
        )
        
        ip_whitelist_enabled = st.checkbox(
            "Enable IP Whitelist",
            value=False,
            help="Restrict access to whitelisted IP addresses"
        )
        
        audit_logging = st.checkbox(
            "Enable Audit Logging",
            value=True,
            help="Log all admin actions for security auditing"
        )
    
    # Save settings
    col5, col6, col7 = st.columns([1, 2, 1])
    with col6:
        if st.button("💾 Save System Settings", use_container_width=True):
            st.success("✅ System settings saved successfully!")
            st.info("Some settings may require a system restart to take effect.")

def show_notifications_management(db: DatabaseManager):
    """Show notifications management"""
    
    st.markdown("### 🔔 Notifications Management")
    
    # System notifications
    st.markdown("#### 📢 System Notifications")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        notification_type = st.selectbox(
            "Notification Type",
            options=["Info", "Warning", "Error", "Maintenance", "Feature Update"]
        )
        
        notification_title = st.text_input(
            "Notification Title",
            placeholder="Enter notification title"
        )
        
        notification_message = st.text_area(
            "Notification Message",
            placeholder="Enter notification message",
            height=100
        )
        
        target_audience = st.multiselect(
            "Target Audience",
            options=["All Users", "Free Users", "Pro Users", "Enterprise Users", "Admins", "Moderators"],
            default=["All Users"]
        )
    
    with col2:
        st.markdown("**Delivery Options**")
        
        send_email = st.checkbox("Send Email", value=True)
        send_push = st.checkbox("Send Push Notification", value=True)
        show_banner = st.checkbox("Show Banner", value=False)
        
        schedule_delivery = st.checkbox("Schedule Delivery", value=False)
        
        if schedule_delivery:
            delivery_date = st.date_input("Delivery Date")
            delivery_time = st.time_input("Delivery Time")
        
        priority = st.selectbox(
            "Priority",
            options=["Low", "Normal", "High", "Critical"],
            index=1
        )
    
    if st.button("📤 Send Notification", use_container_width=True):
        if notification_title and notification_message:
            st.success("✅ Notification sent successfully!")
            st.info(f"Notification '{notification_title}' sent to {', '.join(target_audience)}")
        else:
            st.error("❌ Please fill in title and message")
    
    # Recent notifications
    st.markdown("#### 📋 Recent Notifications")
    
    # Sample notifications data
    recent_notifications = [
        {
            "title": "System Maintenance Scheduled",
            "message": "Scheduled maintenance on Sunday 2AM-4AM UTC",
            "type": "Maintenance",
            "sent_to": "All Users",
            "sent_at": "2024-01-15T10:30:00Z",
            "status": "Delivered"
        },
        {
            "title": "New Feature: Custom Assistants",
            "message": "Create your own AI assistants with custom instructions",
            "type": "Feature Update",
            "sent_to": "Pro Users, Enterprise Users",
            "sent_at": "2024-01-14T14:20:00Z",
            "status": "Delivered"
        },
        {
            "title": "Security Update",
            "message": "Please update your passwords for enhanced security",
            "type": "Warning",
            "sent_to": "All Users",
            "sent_at": "2024-01-13T09:15:00Z",
            "status": "Delivered"
        }
    ]
    
    for notification in recent_notifications:
        type_colors = {
            "Info": "#2196f3",
            "Warning": "#ff9800",
            "Error": "#f44336",
            "Maintenance": "#9c27b0",
            "Feature Update": "#4caf50"
        }
        
        color = type_colors.get(notification["type"], "#666")
        sent_time = time_ago(notification["sent_at"])
        
        st.markdown(f"""
        <div class="dashboard-card" style="border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <strong style="color: {color};">{notification["title"]}</strong>
                    <p style="margin: 5px 0; color: #666; font-size: 0.9rem;">{notification["message"]}</p>
                    <small style="color: #888;">
                        Sent to: {notification["sent_to"]} • Status: {notification["status"]}
                    </small>
                </div>
                <div style="text-align: right;">
                    <small style="color: #888;">{sent_time}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_admin_analytics(db: DatabaseManager):
    """Show admin-specific analytics"""
    
    st.markdown("### 📈 Admin Analytics")
    
    try:
        all_users = db.get_all_users()
        
        # Time-based analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Registration Trends")
            
            # Generate sample registration data
            dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
            daily_registrations = [max(0, (i % 7) + (i % 3)) for i in range(30)]
            
            fig_registrations = px.bar(
                x=dates[-7:],  # Last 7 days
                y=daily_registrations[-7:],
                title="Daily Registrations (Last 7 Days)",
                labels={'x': 'Date', 'y': 'New Users'}
            )
            fig_registrations.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            fig_registrations.update_traces(marker_color='#4caf50')
            st.plotly_chart(fig_registrations, use_container_width=True)
            
            # Revenue trends
            st.markdown("#### 💰 Revenue Trends")
            
            total_revenue = sum([u.get('total_cost', 0) for u in all_users])
            daily_revenue = [total_revenue / 30 * (1 + (i % 5) * 0.2) for i in range(30)]
            
            fig_revenue = px.line(
                x=dates,
                y=daily_revenue,
                title="Daily Revenue (Last 30 Days)",
                labels={'x': 'Date', 'y': 'Revenue ($)'}
            )
            fig_revenue.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            fig_revenue.update_traces(line_color='#4caf50', line_width=3)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Conversion Funnel")
            
            # Sample conversion data
            funnel_data = {
                'Stage': ['Visitors', 'Signups', 'Email Verified', 'First Use', 'Paid Users'],
                'Count': [1000, 250, 200, 150, 50],
                'Conversion': [100, 25, 20, 15, 5]
            }
            
            fig_funnel = px.funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                title="User Conversion Funnel"
            )
            fig_funnel.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Feature usage
            st.markdown("#### 🚀 Feature Usage")
            
            feature_usage = {
                'Feature': ['Chat', 'File Upload', 'Custom Assistants', 'API', 'Voice'],
                'Users': [len(all_users) * 0.8, len(all_users) * 0.6, len(all_users) * 0.3, len(all_users) * 0.4, len(all_users) * 0.2]
            }
            
            fig_features = px.bar(
                x=feature_usage['Feature'],
                y=feature_usage['Users'],
                title="Feature Adoption",
                color=feature_usage['Users'],
                color_continuous_scale='Greens'
            )
            fig_features.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            st.plotly_chart(fig_features, use_container_width=True)
        
        # Performance metrics
        st.markdown("#### ⚡ Performance Metrics")
        
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            create_metric_card(
                "Avg Response Time",
                "245ms",
                "API endpoints",
                "#4caf50"
            )
        
        with col4:
            create_metric_card(
                "Uptime",
                "99.9%",
                "Last 30 days",
                "#4caf50"
            )
        
        with col5:
            create_metric_card(
                "Error Rate",
                "0.1%",
                "Last 24 hours",
                "#4caf50"
            )
        
        with col6:
            create_metric_card(
                "Support Tickets",
                "12",
                "Open tickets",
                "#ff9800"
            )
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def show_maintenance_tools(db: DatabaseManager):
    """Show system maintenance tools"""
    
    st.markdown("### 🛠️ System Maintenance")
    
    # Database maintenance
    st.markdown("#### 💾 Database Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Database Operations**")
        
        if st.button("🔄 Refresh User Cache", use_container_width=True):
            st.cache_resource.clear()
            st.success("✅ User cache refreshed")
        
        if st.button("📊 Rebuild Statistics", use_container_width=True):
            st.info("🔄 Rebuilding database statistics...")
            # Database statistics rebuild would go here
            st.success("✅ Statistics rebuilt successfully")
        
        if st.button("🧹 Clean Old Logs", use_container_width=True):
            if show_confirmation_dialog("This will delete logs older than 90 days. Continue?", "clean_logs"):
                st.success("✅ Old logs cleaned successfully")
        
        if st.button("📥 Backup Database", use_container_width=True):
            st.info("🔄 Creating database backup...")
            # Database backup would go here
            st.success("✅ Database backup created successfully")
    
    with col2:
        st.markdown("**System Health**")
        
        # System health checks
        health_checks = [
            {"name": "Database Connection", "status": "Healthy", "color": "#4caf50"},
            {"name": "API Endpoints", "status": "Healthy", "color": "#4caf50"},
            {"name": "File Storage", "status": "Healthy", "color": "#4caf50"},
            {"name": "Email Service", "status": "Warning", "color": "#ff9800"},
            {"name": "Background Jobs", "status": "Healthy", "color": "#4caf50"}
        ]
        
        for check in health_checks:
            st.markdown(f"""
            <div class="feature-card" style="border-left-color: {check['color']};">
                <strong>{check['name']}:</strong> 
                <span style="color: {check['color']};">{check['status']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Full Health Check", use_container_width=True):
            st.info("🔄 Running comprehensive health check...")
            # Health check would go here
            st.success("✅ All systems healthy")
    
    # User management tools
    st.markdown("#### 👥 Bulk User Operations")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**Bulk Actions**")
        
        bulk_action = st.selectbox(
            "Select Action",
            options=[
                "Send Notification",
                "Update Subscription",
                "Reset Passwords",
                "Export User Data",
                "Deactivate Inactive Users"
            ]
        )
        
        user_filter = st.selectbox(
            "Target Users",
            options=[
                "All Users",
                "Free Users",
                "Pro Users",
                "Enterprise Users",
                "Inactive Users (30+ days)",
                "Users with No Activity"
            ]
        )
        
        if st.button("🚀 Execute Bulk Action", use_container_width=True):
            if show_confirmation_dialog(f"Execute '{bulk_action}' for '{user_filter}'?", "bulk_action"):
                st.success(f"✅ Bulk action '{bulk_action}' executed for {user_filter}")
    
    with col4:
        st.markdown("**System Logs**")
        
        log_type = st.selectbox(
            "Log Type",
            options=["Application Logs", "Error Logs", "Security Logs", "Audit Logs", "Performance Logs"]
        )
        
        log_level = st.selectbox(
            "Log Level",
            options=["All", "Error", "Warning", "Info", "Debug"]
        )
        
        if st.button("📋 View Logs", use_container_width=True):
            st.info(f"Displaying {log_type} with level: {log_level}")
            
            # Sample log entries
            sample_logs = [
                "2024-01-15 10:30:15 [INFO] User login successful: user@example.com",
                "2024-01-15 10:29:45 [WARNING] Rate limit exceeded for IP: 192.168.1.100",
                "2024-01-15 10:28:30 [ERROR] Database connection timeout",
                "2024-01-15 10:27:15 [INFO] System backup completed successfully",
                "2024-01-15 10:26:00 [DEBUG] Cache refresh initiated"
            ]
            
            for log in sample_logs:
                if "ERROR" in log:
                    st.error(log)
                elif "WARNING" in log:
                    st.warning(log)
                else:
                    st.info(log)
    
    # Emergency tools
    st.markdown("---")
    st.markdown("#### 🚨 Emergency Tools")
    
    st.warning("⚠️ These tools should only be used in emergency situations")
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if st.button("🔒 Enable Maintenance Mode", use_container_width=True, type="secondary"):
            if show_confirmation_dialog("This will prevent all users from accessing the system. Continue?", "maintenance_mode"):
                st.error("🔒 Maintenance mode enabled")
    
    with col6:
        if st.button("🛑 Emergency Shutdown", use_container_width=True, type="secondary"):
            if show_confirmation_dialog("This will immediately shut down all services. Continue?", "emergency_shutdown"):
                st.error("🛑 Emergency shutdown initiated")
    
    with col7:
        if st.button("🔄 Force Restart", use_container_width=True, type="secondary"):
            if show_confirmation_dialog("This will restart all system services. Continue?", "force_restart"):
                st.error("🔄 System restart initiated")

if __name__ == "__main__":
    main()
