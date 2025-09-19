import streamlit as st
import sys
import os

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.auth import AuthManager
from components.database import DatabaseManager
from components.ui_components import (
    load_custom_css, create_metric_card, show_alert,
    create_user_card, show_confirmation_dialog, safe_date_format,
    calculate_activity_score, get_activity_class
)
from components.utils import (
    format_currency, time_ago, filter_users, paginate_data,
    get_role_color, get_status_color, export_data_to_csv
)
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="User Management",
    page_icon="👥",
    layout="wide"
)

def main():
    """Main user management page"""
    
    # Load custom styling
    load_custom_css()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Require admin authentication
    auth_manager.require_role('admin')
    
    # Initialize database manager with service role
    db = DatabaseManager(use_service_role=True)
    
    # Page header
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="color: #2e7d32; margin-bottom: 0.5rem;">👥 User Management</h1>
        <p style="color: #666; font-size: 1.1rem;">Comprehensive user administration and management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all users
    with st.spinner("Loading user data..."):
        all_users = db.get_all_users()
    
    if not all_users:
        st.error("❌ No user data available or failed to load users")
        return
    
    # User management tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "👥 All Users", 
        "⏳ Pending Approvals", 
        "📈 Analytics", 
        "🔧 Bulk Operations"
    ])
    
    with tab1:
        show_users_overview(all_users)
    
    with tab2:
        show_all_users(all_users, db)
    
    with tab3:
        show_pending_approvals(all_users, db)
    
    with tab4:
        show_user_analytics(all_users)
    
    with tab5:
        show_bulk_operations(all_users, db)

def show_users_overview(users: List[Dict]):
    """Show comprehensive user overview with statistics"""
    
    st.markdown("### 📊 User Overview")
    
    # Calculate comprehensive statistics
    total_users = len(users)
    admin_users = len([u for u in users if u.get('role') == 'admin'])
    moderator_users = len([u for u in users if u.get('role') == 'moderator'])
    active_users = len([u for u in users if u.get('is_active', True)])
    verified_users = len([u for u in users if u.get('email_confirmed_at')])
    pending_approvals = len([u for u in users if u.get('pending_approval', False)])
    
    # Subscription stats
    free_users = len([u for u in users if u.get('subscription_tier') == 'free'])
    pro_users = len([u for u in users if u.get('subscription_tier') == 'pro'])
    enterprise_users = len([u for u in users if u.get('subscription_tier') == 'enterprise'])
    
    # Activity stats
    active_today = len([u for u in users if calculate_activity_score(u.get('last_sign_in_at', '')) == "Today"])
    active_week = len([u for u in users if calculate_activity_score(u.get('last_sign_in_at', '')) in ["Today", "Yesterday"] or "days ago" in calculate_activity_score(u.get('last_sign_in_at', ''))])
    
    # Revenue and usage
    total_revenue = sum([u.get('total_cost', 0) for u in users])
    total_tokens = sum([u.get('tokens_used', 0) for u in users])
    total_api_requests = sum([u.get('api_requests', 0) for u in users])
    
    # Main stats cards
    st.markdown("#### 📈 Key Metrics")
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
            "Admins",
            str(admin_users),
            f"{moderator_users} moderators",
            "#ff9800"
        )
    
    with col3:
        create_metric_card(
            "Verified",
            str(verified_users),
            f"{(verified_users/max(total_users,1)*100):.1f}% of total",
            "#4caf50"
        )
    
    with col4:
        create_metric_card(
            "Pending",
            str(pending_approvals),
            "Awaiting approval",
            "#ff9800" if pending_approvals > 0 else "#4caf50"
        )
    
    with col5:
        create_metric_card(
            "Active Today",
            str(active_today),
            f"{active_week} this week",
            "#4caf50"
        )
    
    with col6:
        create_metric_card(
            "Total Revenue",
            format_currency(total_revenue),
            "All time",
            "#2e7d32"
        )
    
    # Subscription and usage stats
    st.markdown("#### 💰 Subscription & Usage Analytics")
    col7, col8, col9, col10, col11, col12 = st.columns(6)
    
    with col7:
        create_metric_card(
            "Free Users",
            str(free_users),
            f"{(free_users/max(total_users,1)*100):.1f}%",
            "#4caf50"
        )
    
    with col8:
        create_metric_card(
            "Pro Users",
            str(pro_users),
            f"{(pro_users/max(total_users,1)*100):.1f}%",
            "#ff9800"
        )
    
    with col9:
        create_metric_card(
            "Enterprise",
            str(enterprise_users),
            f"{(enterprise_users/max(total_users,1)*100):.1f}%",
            "#9c27b0"
        )
    
    with col10:
        create_metric_card(
            "Total Tokens",
            f"{total_tokens:,}",
            "All users",
            "#2e7d32"
        )
    
    with col11:
        create_metric_card(
            "API Requests",
            f"{total_api_requests:,}",
            "All time",
            "#2e7d32"
        )
    
    with col12:
        avg_revenue = total_revenue / max(total_users, 1)
        create_metric_card(
            "Avg Revenue",
            format_currency(avg_revenue),
            "Per user",
            "#2e7d32"
        )
    
    # Visual analytics
    if users:
        st.markdown("#### 📊 Visual Analytics")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Role distribution pie chart
            role_counts = {}
            for user in users:
                role = user.get('role', 'user')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            fig_roles = px.pie(
                values=list(role_counts.values()),
                names=list(role_counts.keys()),
                title="User Role Distribution",
                color_discrete_sequence=['#4caf50', '#ff9800', '#9c27b0', '#f44336']
            )
            fig_roles.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        
        with chart_col2:
            # Subscription tier distribution
            tier_counts = {'free': free_users, 'pro': pro_users, 'enterprise': enterprise_users}
            
            fig_tiers = px.bar(
                x=list(tier_counts.keys()),
                y=list(tier_counts.values()),
                title="Subscription Tier Distribution",
                color=list(tier_counts.keys()),
                color_discrete_sequence=['#4caf50', '#ff9800', '#9c27b0']
            )
            fig_tiers.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                xaxis_title="Subscription Tier",
                yaxis_title="Number of Users"
            )
            st.plotly_chart(fig_tiers, use_container_width=True)

def show_all_users(users: List[Dict], db: DatabaseManager):
    """Show all users with filtering and management options"""
    
    st.markdown("### 👥 All Users")
    
    # Filters
    st.markdown("#### 🔍 Filters")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        role_filter = st.selectbox("Role", ["All", "admin", "moderator", "user"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
    with col3:
        tier_filter = st.selectbox("Subscription Tier", ["All", "free", "pro", "enterprise"])
    with col4:
        activity_filter = st.selectbox("Activity Level", ["All", "Active Today", "Active This Week", "Inactive"])
    with col5:
        search_term = st.text_input("🔍 Search users...")
    
    # Apply filters
    filters = {
        'role': role_filter,
        'status': status_filter,
        'subscription_tier': tier_filter,
        'search_term': search_term
    }
    
    filtered_users = filter_users(users, filters)
    
    # Additional activity filter
    if activity_filter != "All":
        if activity_filter == "Active Today":
            filtered_users = [u for u in filtered_users if calculate_activity_score(u.get('last_sign_in_at', '')) == "Today"]
        elif activity_filter == "Active This Week":
            filtered_users = [u for u in filtered_users if calculate_activity_score(u.get('last_sign_in_at', '')) in ["Today", "Yesterday"] or "days ago" in calculate_activity_score(u.get('last_sign_in_at', ''))]
        elif activity_filter == "Inactive":
            filtered_users = [u for u in filtered_users if calculate_activity_score(u.get('last_sign_in_at', '')) in ["Never"] or "months ago" in calculate_activity_score(u.get('last_sign_in_at', '')) or "years ago" in calculate_activity_score(u.get('last_sign_in_at', ''))]
    
    st.markdown(f"**Showing {len(filtered_users)} of {len(users)} users**")
    
    # Pagination
    users_per_page = 10
    pagination_data = paginate_data(filtered_users, 1, users_per_page)
    
    if pagination_data['total_pages'] > 1:
        page = st.selectbox("Page", range(1, pagination_data['total_pages'] + 1))
        pagination_data = paginate_data(filtered_users, page, users_per_page)
    
    # Export options
    col_export1, col_export2, col_export3 = st.columns([1, 1, 4])
    
    with col_export1:
        if st.button("📥 Export CSV"):
            csv_data = export_data_to_csv(filtered_users, "users_export.csv")
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col_export2:
        if st.button("📊 Generate Report"):
            st.info("Detailed user report would be generated here")
    
    # Show user cards
    for user in pagination_data['data']:
        render_enhanced_user_card(user, db)

def render_enhanced_user_card(user: Dict, db: DatabaseManager):
    """Render an enhanced user card with all management options"""
    
    # Determine card class based on user role and status
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
    
    # Format data
    created_date = safe_date_format(user.get('created_at', ''), '%Y-%m-%d')
    last_login = safe_date_format(user.get('last_sign_in_at', ''), '%Y-%m-%d %H:%M')
    activity_score = calculate_activity_score(user.get('last_sign_in_at', ''))
    activity_class = get_activity_class(activity_score)
    role_color = get_role_color(user.get('role', 'user'))
    
    # Create expandable user card
    with st.expander(f"👤 {user.get('full_name', 'Unnamed User')} ({user.get('email', 'No email')})", expanded=False):
        
        # Main user info
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            st.markdown("**Basic Information:**")
            st.write(f"• **User ID:** {user.get('id', 'N/A')[:8]}...")
            st.write(f"• **Username:** {user.get('username', 'Not set')}")
            st.write(f"• **Full Name:** {user.get('full_name', 'Not set')}")
            st.write(f"• **Email:** {user.get('email', 'No email')}")
            if user.get('website'):
                st.write(f"• **Website:** [Link]({user['website']})")
        
        with col2:
            st.markdown("**Account Details:**")
            st.write(f"• **Role:** {user.get('role', 'user').title()}")
            st.write(f"• **Subscription:** {user.get('subscription_tier', 'free').title()}")
            st.write(f"• **Status:** {'Active' if user.get('is_active', True) else 'Inactive'}")
            st.write(f"• **Email Verified:** {'Yes' if user.get('email_confirmed_at') else 'No'}")
            st.write(f"• **Created:** {created_date}")
        
        with col3:
            st.markdown("**Usage Statistics:**")
            st.write(f"• **Tokens Used:** {user.get('tokens_used', 0):,}")
            st.write(f"• **Total Cost:** {format_currency(user.get('total_cost', 0))}")
            st.write(f"• **API Requests:** {user.get('api_requests', 0):,}")
            st.write(f"• **Chat Threads:** {user.get('chat_threads_count', 0)}")
            st.write(f"• **File Uploads:** {user.get('file_uploads_count', 0)}")
        
        with col4:
            st.markdown("**Activity & Features:**")
            st.write(f"• **Last Login:** {activity_score}")
            st.write(f"• **Activity Logs:** {user.get('activity_logs_count', 0)}")
            st.write(f"• **Custom Assistants:** {user.get('custom_assistants_count', 0)}")
            st.write(f"• **Voice Enabled:** {'Yes' if user.get('voice_enabled') else 'No'}")
            st.write(f"• **Advanced Features:** {'Yes' if user.get('advanced_features') else 'No'}")
        
        # Detailed tabs
        detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(["🔧 Actions", "📊 Analytics", "🔒 Security", "📋 Logs"])
        
        with detail_tab1:
            show_user_actions(user, db)
        
        with detail_tab2:
            show_user_analytics_detail(user)
        
        with detail_tab3:
            show_user_security_detail(user)
        
        with detail_tab4:
            show_user_logs_detail(user)

def show_user_actions(user: Dict, db: DatabaseManager):
    """Show user management actions"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Account Management**")
        
        # Role management
        current_role = user.get('role', 'user')
        new_role = st.selectbox(
            "Change Role",
            options=['user', 'moderator', 'admin'],
            index=['user', 'moderator', 'admin'].index(current_role),
            key=f"role_{user['id']}"
        )
        
        if new_role != current_role:
            if st.button(f"Update Role to {new_role.title()}", key=f"update_role_{user['id']}"):
                if db.update_user_role(user['id'], new_role):
                    st.success(f"✅ Role updated to {new_role}")
                    st.rerun()
                else:
                    st.error("❌ Failed to update role")
        
        # Account status
        if user.get('is_active', True):
            if st.button("🔒 Deactivate Account", key=f"deactivate_{user['id']}", type="secondary"):
                if show_confirmation_dialog(f"Deactivate account for {user.get('email', 'user')}?", f"deactivate_{user['id']}"):
                    st.success("✅ Account deactivated")
        else:
            if st.button("✅ Activate Account", key=f"activate_{user['id']}"):
                st.success("✅ Account activated")
    
    with col2:
        st.markdown("**Approval Actions**")
        
        if user.get('pending_approval', False):
            col2a, col2b = st.columns(2)
            
            with col2a:
                if st.button("✅ Approve", key=f"approve_{user['id']}"):
                    if db.approve_user(user['id'], user.get('email', '')):
                        st.success("✅ User approved")
                        st.rerun()
                    else:
                        st.error("❌ Failed to approve user")
            
            with col2b:
                if st.button("❌ Reject", key=f"reject_{user['id']}", type="secondary"):
                    if show_confirmation_dialog(f"Reject user {user.get('email', 'user')}?", f"reject_{user['id']}"):
                        if db.reject_user(user['id'], user.get('email', '')):
                            st.success("✅ User rejected")
                            st.rerun()
                        else:
                            st.error("❌ Failed to reject user")
        else:
            st.info("No pending approvals for this user")
        
        # Send notification
        if st.button("📧 Send Notification", key=f"notify_{user['id']}"):
            st.info("Notification functionality would be implemented here")
    
    with col3:
        st.markdown("**Data Management**")
        
        if st.button("📥 Export User Data", key=f"export_{user['id']}"):
            st.info("User data export would be generated here")
        
        if st.button("🔄 Reset Password", key=f"reset_pwd_{user['id']}"):
            st.info("Password reset email would be sent")
        
        if st.button("🗑️ Delete Account", key=f"delete_{user['id']}", type="secondary"):
            if show_confirmation_dialog(f"Permanently delete account for {user.get('email', 'user')}? This cannot be undone.", f"delete_{user['id']}"):
                st.error("Account deletion would be processed here")

def show_user_analytics_detail(user: Dict):
    """Show detailed user analytics"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Usage breakdown
        st.markdown("**Usage Breakdown**")
        
        usage_data = {
            'Category': ['Tokens', 'API Requests', 'Chat Threads', 'File Uploads', 'Custom Assistants'],
            'Count': [
                user.get('tokens_used', 0),
                user.get('api_requests', 0),
                user.get('chat_threads_count', 0),
                user.get('file_uploads_count', 0),
                user.get('custom_assistants_count', 0)
            ]
        }
        
        if sum(usage_data['Count']) > 0:
            fig_usage = px.bar(
                x=usage_data['Category'],
                y=usage_data['Count'],
                title=f"Usage Statistics for {user.get('full_name', 'User')}",
                color=usage_data['Count'],
                color_continuous_scale='Greens'
            )
            fig_usage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig_usage, use_container_width=True)
        else:
            st.info("No usage data available for this user")
    
    with col2:
        # Cost analysis
        st.markdown("**Cost Analysis**")
        
        total_cost = user.get('total_cost', 0)
        
        if total_cost > 0:
            cost_breakdown = {
                'API Calls': total_cost * 0.7,
                'Storage': total_cost * 0.2,
                'Features': total_cost * 0.1
            }
            
            fig_cost = px.pie(
                values=list(cost_breakdown.values()),
                names=list(cost_breakdown.keys()),
                title="Cost Breakdown"
            )
            fig_cost.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                height=300
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("No cost data available for this user")

def show_user_security_detail(user: Dict):
    """Show user security details"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Security Information**")
        
        st.write(f"• **Account Created:** {safe_date_format(user.get('created_at', ''), '%B %d, %Y at %I:%M %p')}")
        st.write(f"• **Email Verified:** {'Yes' if user.get('email_confirmed_at') else 'No'}")
        st.write(f"• **Last Login:** {safe_date_format(user.get('last_sign_in_at', ''), '%B %d, %Y at %I:%M %p')}")
        st.write(f"• **Two-Factor Auth:** {'Enabled' if user.get('two_factor_enabled') else 'Disabled'}")
        st.write(f"• **Failed Login Attempts:** {user.get('failed_login_attempts', 0)}")
        
        # Security score
        security_score = 0
        if user.get('email_confirmed_at'):
            security_score += 25
        if user.get('two_factor_enabled'):
            security_score += 25
        if user.get('last_sign_in_at'):
            security_score += 25
        if len(user.get('password', '')) >= 8:  # Placeholder check
            security_score += 25
        
        st.write(f"• **Security Score:** {security_score}/100")
    
    with col2:
        st.markdown("**Security Actions**")
        
        if st.button("🔒 Force Password Reset", key=f"force_reset_{user['id']}"):
            st.info("Password reset would be forced for this user")
        
        if st.button("📱 Reset 2FA", key=f"reset_2fa_{user['id']}"):
            st.info("Two-factor authentication would be reset")
        
        if st.button("🚫 Revoke Sessions", key=f"revoke_sessions_{user['id']}"):
            st.info("All active sessions would be revoked")
        
        if st.button("🔍 Security Audit", key=f"audit_{user['id']}"):
            st.info("Security audit would be performed")

def show_user_logs_detail(user: Dict):
    """Show user activity logs"""
    
    # Sample activity logs (in real app, this would come from database)
    sample_activities = user.get('recent_activities', [])
    
    if sample_activities:
        st.markdown("**Recent Activity Logs**")
        
        for activity in sample_activities[-10:]:  # Show last 10
            activity_time = safe_date_format(activity.get('created_at', ''), '%B %d, %Y at %I:%M %p')
            activity_type = activity.get('activity_type', 'Unknown').replace('_', ' ').title()
            description = activity.get('description', 'No description')
            
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-left: 4px solid #4caf50; border-radius: 5px;">
                <strong>{activity_type}</strong> - {activity_time}<br>
                <small style="color: #666;">{description}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity logs available for this user")
    
    # Log export
    if st.button("📥 Export Full Activity Log", key=f"export_logs_{user['id']}"):
        st.info("Full activity log export would be generated here")

def show_pending_approvals(users: List[Dict], db: DatabaseManager):
    """Show pending user approvals"""
    
    st.markdown("### ⏳ Pending Approvals")
    
    pending_users = [u for u in users if u.get('pending_approval', False)]
    
    if pending_users:
        st.markdown(f"**{len(pending_users)} users awaiting approval**")
        
        # Bulk approval actions
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("✅ Approve All"):
                if show_confirmation_dialog(f"Approve all {len(pending_users)} pending users?", "approve_all"):
                    approved_count = 0
                    for user in pending_users:
                        if db.approve_user(user['id'], user.get('email', '')):
                            approved_count += 1
                    st.success(f"✅ Approved {approved_count} users")
                    st.rerun()
        
        with col2:
            if st.button("❌ Reject All", type="secondary"):
                if show_confirmation_dialog(f"Reject all {len(pending_users)} pending users?", "reject_all"):
                    rejected_count = 0
                    for user in pending_users:
                        if db.reject_user(user['id'], user.get('email', '')):
                            rejected_count += 1
                    st.success(f"✅ Rejected {rejected_count} users")
                    st.rerun()
        
        # Individual pending users
        for user in pending_users:
            render_pending_user_card(user, db)
    else:
        st.success("🎉 No pending approvals!")
        st.info("All users have been processed. New registrations will appear here.")

def render_pending_user_card(user: Dict, db: DatabaseManager):
    """Render a card for pending user approval"""
    
    created_date = safe_date_format(user.get('created_at', ''), '%B %d, %Y at %I:%M %p')
    
    st.markdown(f"""
    <div class="pending-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
            <div>
                <h4 style="margin: 0; color: #333;">{user.get('full_name', 'Unnamed User')}</h4>
                <p style="margin: 5px 0; color: #666;">{user.get('email', 'No email')}</p>
                <small style="color: #888;">Registered: {created_date}</small>
            </div>
            <div>
                <span style="background: #f44336; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem;">
                    Pending Approval
                </span>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
            <div>
                <p style="margin: 0; color: #666; font-size: 0.9rem;"><strong>Subscription:</strong> {user.get('subscription_tier', 'free').title()}</p>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;"><strong>Email Verified:</strong> {'Yes' if user.get('email_confirmed_at') else 'No'}</p>
            </div>
            <div>
                <p style="margin: 0; color: #666; font-size: 0.9rem;"><strong>User ID:</strong> {user.get('id', 'N/A')[:8]}...</p>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;"><strong>Username:</strong> {user.get('username', 'Not set')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Approve", key=f"approve_pending_{user['id']}"):
            if db.approve_user(user['id'], user.get('email', '')):
                st.success("✅ User approved")
                st.rerun()
            else:
                st.error("❌ Failed to approve user")
    
    with col2:
        if st.button("❌ Reject", key=f"reject_pending_{user['id']}", type="secondary"):
            if show_confirmation_dialog(f"Reject user {user.get('email', 'user')}?", f"reject_pending_{user['id']}"):
                if db.reject_user(user['id'], user.get('email', '')):
                    st.success("✅ User rejected")
                    st.rerun()
                else:
                    st.error("❌ Failed to reject user")
    
    with col3:
        if st.button("📧 Contact", key=f"contact_pending_{user['id']}"):
            st.info("Contact functionality would be implemented here")
    
    with col4:
        if st.button("📋 Details", key=f"details_pending_{user['id']}"):
            st.info("Detailed view would be shown here")

def show_user_analytics(users: List[Dict]):
    """Show comprehensive user analytics"""
    
    st.markdown("### 📈 User Analytics")
    
    if not users:
        st.warning("No user data available for analytics")
        return
    
    # Time-based analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # User registration trends
        st.markdown("#### 📅 Registration Trends")
        
        # Generate sample registration data based on user creation dates
        dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
        daily_registrations = [max(0, len(users) // 30 + (i % 7)) for i in range(30)]
        
        fig_registrations = px.line(
            x=dates,
            y=daily_registrations,
            title="Daily Registrations (Last 30 Days)",
            labels={'x': 'Date', 'y': 'New Registrations'}
        )
        fig_registrations.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_registrations.update_traces(line_color='#4caf50', line_width=3)
        st.plotly_chart(fig_registrations, use_container_width=True)
        
        # Activity heatmap
        st.markdown("#### 🔥 Activity Heatmap")
        
        # Sample activity data
        activity_data = []
        for user in users[:20]:  # Sample of users
            activity_data.append({
                'User': user.get('full_name', 'User')[:15],
                'Tokens': user.get('tokens_used', 0),
                'Threads': user.get('chat_threads_count', 0),
                'Files': user.get('file_uploads_count', 0)
            })
        
        if activity_data:
            df_activity = pd.DataFrame(activity_data)
            fig_heatmap = px.imshow(
                df_activity.set_index('User').T,
                title="User Activity Heatmap",
                color_continuous_scale='Greens'
            )
            fig_heatmap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                height=400
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Revenue analysis
        st.markdown("#### 💰 Revenue Analysis")
        
        total_revenue = sum([u.get('total_cost', 0) for u in users])
        monthly_revenue = [total_revenue / 12 * (1 + (i % 4) * 0.1) for i in range(12)]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig_revenue = px.bar(
            x=months,
            y=monthly_revenue,
            title="Monthly Revenue Projection",
            labels={'x': 'Month', 'y': 'Revenue ($)'},
            color=monthly_revenue,
            color_continuous_scale='Greens'
        )
        fig_revenue.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # User segmentation
        st.markdown("#### 🎯 User Segmentation")
        
        # Segment users by usage
        segments = {'High Value': 0, 'Medium Value': 0, 'Low Value': 0, 'Inactive': 0}
        
        for user in users:
            cost = user.get('total_cost', 0)
            if cost > 50:
                segments['High Value'] += 1
            elif cost > 10:
                segments['Medium Value'] += 1
            elif cost > 0:
                segments['Low Value'] += 1
            else:
                segments['Inactive'] += 1
        
        fig_segments = px.pie(
            values=list(segments.values()),
            names=list(segments.keys()),
            title="User Value Segmentation"
        )
        fig_segments.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        st.plotly_chart(fig_segments, use_container_width=True)

def show_bulk_operations(users: List[Dict], db: DatabaseManager):
    """Show bulk operations interface"""
    
    st.markdown("### 🔧 Bulk Operations")
    
    st.warning("⚠️ Bulk operations affect multiple users. Use with caution.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Bulk Actions")
        
        # Select users for bulk operations
        bulk_filter = st.selectbox(
            "Select Users",
            options=[
                "All Users",
                "Free Users",
                "Pro Users", 
                "Enterprise Users",
                "Inactive Users (30+ days)",
                "Unverified Users",
                "Pending Approval Users"
            ]
        )
        
        # Filter users based on selection
        if bulk_filter == "Free Users":
            target_users = [u for u in users if u.get('subscription_tier') == 'free']
        elif bulk_filter == "Pro Users":
            target_users = [u for u in users if u.get('subscription_tier') == 'pro']
        elif bulk_filter == "Enterprise Users":
            target_users = [u for u in users if u.get('subscription_tier') == 'enterprise']
        elif bulk_filter == "Inactive Users (30+ days)":
            target_users = [u for u in users if 'months ago' in calculate_activity_score(u.get('last_sign_in_at', '')) or 'years ago' in calculate_activity_score(u.get('last_sign_in_at', ''))]
        elif bulk_filter == "Unverified Users":
            target_users = [u for u in users if not u.get('email_confirmed_at')]
        elif bulk_filter == "Pending Approval Users":
            target_users = [u for u in users if u.get('pending_approval', False)]
        else:
            target_users = users
        
        st.info(f"Selected: {len(target_users)} users")
        
        # Bulk actions
        bulk_action = st.selectbox(
            "Select Action",
            options=[
                "Send Email Notification",
                "Update Subscription Tier",
                "Reset Passwords",
                "Export User Data",
                "Deactivate Accounts",
                "Approve Pending Users",
                "Send Welcome Email"
            ]
        )
        
        # Action-specific parameters
        if bulk_action == "Send Email Notification":
            email_subject = st.text_input("Email Subject")
            email_body = st.text_area("Email Body", height=100)
        elif bulk_action == "Update Subscription Tier":
            new_tier = st.selectbox("New Tier", ["free", "pro", "enterprise"])
        
        # Execute bulk action
        if st.button("🚀 Execute Bulk Action", type="primary"):
            if show_confirmation_dialog(f"Execute '{bulk_action}' for {len(target_users)} users?", "bulk_execute"):
                st.success(f"✅ Bulk action '{bulk_action}' executed for {len(target_users)} users")
                st.info("In a real implementation, this would process all selected users")
    
    with col2:
        st.markdown("#### 📊 Bulk Statistics")
        
        # Show statistics for selected users
        if target_users:
            total_revenue = sum([u.get('total_cost', 0) for u in target_users])
            total_tokens = sum([u.get('tokens_used', 0) for u in target_users])
            avg_activity = len([u for u in target_users if calculate_activity_score(u.get('last_sign_in_at', '')) in ['Today', 'Yesterday']]) / len(target_users) * 100
            
            create_metric_card(
                "Selected Users",
                str(len(target_users)),
                f"of {len(users)} total"
            )
            
            create_metric_card(
                "Total Revenue",
                format_currency(total_revenue),
                "From selected users"
            )
            
            create_metric_card(
                "Total Tokens",
                f"{total_tokens:,}",
                "Used by selected users"
            )
            
            create_metric_card(
                "Active Users",
                f"{avg_activity:.1f}%",
                "Recently active"
            )
        
        st.markdown("#### 📋 Recent Bulk Operations")
        
        # Sample recent operations
        recent_operations = [
            {
                "action": "Send Welcome Email",
                "users": 25,
                "date": "2024-01-15 10:30:00",
                "status": "Completed"
            },
            {
                "action": "Export User Data",
                "users": 150,
                "date": "2024-01-14 14:20:00", 
                "status": "Completed"
            },
            {
                "action": "Reset Passwords",
                "users": 5,
                "date": "2024-01-13 09:15:00",
                "status": "Completed"
            }
        ]
        
        for op in recent_operations:
            st.markdown(f"""
            <div class="feature-card">
                <strong>{op['action']}</strong><br>
                <small style="color: #666;">
                    {op['users']} users • {time_ago(op['date'])} • Status: {op['status']}
                </small>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
