import streamlit as st
import sys
import os

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.auth import AuthManager
from components.database import DatabaseManager
from components.ui_components import (
    load_custom_css, create_metric_card, create_progress_bar,
    safe_date_format, time_ago
)
from components.utils import (
    calculate_usage_percentage, get_subscription_limits,
    format_currency, generate_activity_summary
)
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Usage Analytics",
    page_icon="📊",
    layout="wide"
)

def main():
    """Main usage analytics page"""
    
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
        <h1 style="color: #2e7d32; margin-bottom: 0.5rem;">📊 Usage Analytics</h1>
        <p style="color: #666; font-size: 1.1rem;">Detailed insights into your platform usage and activity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user statistics
    usage_stats = db.get_user_usage_stats(user_id) if user_id else {}
    activity_logs = db.get_user_activity_logs(user_id, limit=100) if user_id else []
    
    # Main analytics sections
    show_usage_overview(user_data, usage_stats)
    
    st.markdown("---")
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Usage Trends", "💰 Cost Analysis", "🔄 Activity Timeline", "📋 Detailed Reports"])
    
    with tab1:
        show_usage_trends(user_data, usage_stats, activity_logs)
    
    with tab2:
        show_cost_analysis(user_data, usage_stats)
    
    with tab3:
        show_activity_timeline(activity_logs)
    
    with tab4:
        show_detailed_reports(user_data, usage_stats, activity_logs)

def show_usage_overview(user_data: Dict, usage_stats: Dict):
    """Show usage overview with key metrics"""
    
    st.markdown("### 📊 Usage Overview")
    
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
    
    assistant_usage = calculate_usage_percentage(
        usage_stats.get('custom_assistants_count', 0), 
        limits['max_assistants']
    )
    
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card(
            "Total Tokens",
            f"{usage_stats.get('total_tokens', 0):,}",
            f"of {limits['monthly_tokens']:,}",
            "#4caf50" if token_usage < 80 else "#ff9800" if token_usage < 95 else "#f44336"
        )
    
    with col2:
        create_metric_card(
            "API Requests",
            f"{usage_stats.get('total_requests', 0):,}",
            "This month",
            "#2e7d32"
        )
    
    with col3:
        create_metric_card(
            "Total Cost",
            format_currency(usage_stats.get('total_cost', 0)),
            "This month",
            "#4caf50"
        )
    
    with col4:
        create_metric_card(
            "Chat Threads",
            str(usage_stats.get('chat_threads_count', 0)),
            f"of {limits['max_threads']} max",
            "#4caf50" if thread_usage < 80 else "#ff9800"
        )
    
    with col5:
        create_metric_card(
            "File Uploads",
            str(usage_stats.get('file_uploads_count', 0)),
            f"of {limits['max_files']} max",
            "#4caf50" if file_usage < 80 else "#ff9800"
        )
    
    # Usage progress bars
    st.markdown("#### 📈 Resource Usage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_progress_bar(
            token_usage,
            f"Token Usage ({usage_stats.get('total_tokens', 0):,} / {limits['monthly_tokens']:,})",
            "#4caf50" if token_usage < 80 else "#ff9800" if token_usage < 95 else "#f44336"
        )
        
        create_progress_bar(
            file_usage,
            f"File Storage ({usage_stats.get('file_uploads_count', 0)} / {limits['max_files']})",
            "#4caf50" if file_usage < 80 else "#ff9800"
        )
    
    with col2:
        create_progress_bar(
            thread_usage,
            f"Chat Threads ({usage_stats.get('chat_threads_count', 0)} / {limits['max_threads']})",
            "#4caf50" if thread_usage < 80 else "#ff9800"
        )
        
        create_progress_bar(
            assistant_usage,
            f"Custom Assistants ({usage_stats.get('custom_assistants_count', 0)} / {limits['max_assistants']})",
            "#4caf50" if assistant_usage < 80 else "#ff9800"
        )

def show_usage_trends(user_data: Dict, usage_stats: Dict, activity_logs: List[Dict]):
    """Show usage trends and patterns"""
    
    st.markdown("### 📈 Usage Trends")
    
    # Generate sample data for demonstration
    # In a real application, this would come from actual usage data
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
    
    # Token usage trend
    base_usage = usage_stats.get('total_tokens', 0) // 30
    token_usage_daily = [max(0, base_usage + (i % 7) * 100 + (i % 3) * 50) for i in range(30)]
    
    # API requests trend
    base_requests = usage_stats.get('total_requests', 0) // 30
    api_requests_daily = [max(0, base_requests + (i % 5) * 10 + (i % 2) * 5) for i in range(30)]
    
    # Cost trend
    cost_daily = [usage_stats.get('total_cost', 0) / 30 * (1 + (i % 7) * 0.1) for i in range(30)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Token usage chart
        fig_tokens = px.line(
            x=dates,
            y=token_usage_daily,
            title="Daily Token Usage (Last 30 Days)",
            labels={'x': 'Date', 'y': 'Tokens Used'}
        )
        fig_tokens.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_tokens.update_traces(line_color='#4caf50', line_width=3)
        st.plotly_chart(fig_tokens, use_container_width=True)
        
        # Cost trend chart
        fig_cost = px.area(
            x=dates,
            y=cost_daily,
            title="Daily Cost Trend (Last 30 Days)",
            labels={'x': 'Date', 'y': 'Cost ($)'}
        )
        fig_cost.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_cost.update_traces(fill='tonexty', fillcolor='rgba(76, 175, 80, 0.3)', line_color='#4caf50')
        st.plotly_chart(fig_cost, use_container_width=True)
    
    with col2:
        # API requests chart
        fig_requests = px.bar(
            x=dates[-7:],  # Last 7 days
            y=api_requests_daily[-7:],
            title="API Requests (Last 7 Days)",
            labels={'x': 'Date', 'y': 'Requests'}
        )
        fig_requests.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_requests.update_traces(marker_color='#4caf50')
        st.plotly_chart(fig_requests, use_container_width=True)
        
        # Activity distribution
        if activity_logs:
            activity_types = {}
            for log in activity_logs:
                activity_type = log.get('activity_type', 'Unknown')
                activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
            
            fig_activity = px.pie(
                values=list(activity_types.values()),
                names=list(activity_types.keys()),
                title="Activity Distribution"
            )
            fig_activity.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        else:
            st.info("No activity data available yet.")
    
    # Usage patterns
    st.markdown("#### 🕐 Usage Patterns")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Hourly usage pattern (sample data)
        hours = list(range(24))
        hourly_usage = [max(0, 100 + 50 * abs(12 - h) + (h % 3) * 20) for h in hours]
        
        fig_hourly = px.bar(
            x=hours,
            y=hourly_usage,
            title="Usage by Hour of Day",
            labels={'x': 'Hour', 'y': 'Activity Level'}
        )
        fig_hourly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_hourly.update_traces(marker_color='#4caf50')
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col4:
        # Weekly usage pattern (sample data)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekly_usage = [80, 90, 85, 95, 88, 60, 45]
        
        fig_weekly = px.bar(
            x=days,
            y=weekly_usage,
            title="Usage by Day of Week",
            labels={'x': 'Day', 'y': 'Activity Level'}
        )
        fig_weekly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            showlegend=False
        )
        fig_weekly.update_traces(marker_color='#4caf50')
        st.plotly_chart(fig_weekly, use_container_width=True)

def show_cost_analysis(user_data: Dict, usage_stats: Dict):
    """Show detailed cost analysis"""
    
    st.markdown("### 💰 Cost Analysis")
    
    total_cost = usage_stats.get('total_cost', 0)
    
    if total_cost > 0:
        # Cost breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost breakdown pie chart
            cost_breakdown = {
                'API Calls': total_cost * 0.7,
                'Storage': total_cost * 0.15,
                'Features': total_cost * 0.10,
                'Other': total_cost * 0.05
            }
            
            fig_breakdown = px.pie(
                values=list(cost_breakdown.values()),
                names=list(cost_breakdown.keys()),
                title="Cost Breakdown This Month"
            )
            fig_breakdown.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_breakdown, use_container_width=True)
        
        with col2:
            # Cost per feature
            st.markdown("#### 💳 Cost Details")
            
            st.markdown(f"""
            <div class="feature-card">
                <strong>Total This Month:</strong> {format_currency(total_cost)}<br>
                <strong>Average Daily:</strong> {format_currency(total_cost / 30)}<br>
                <strong>Cost per Token:</strong> ${(total_cost / max(usage_stats.get('total_tokens', 1), 1)):.6f}<br>
                <strong>Cost per Request:</strong> {format_currency(total_cost / max(usage_stats.get('total_requests', 1), 1))}
            </div>
            """, unsafe_allow_html=True)
            
            # Projected costs
            subscription_tier = user_data.get('subscription_tier', 'free')
            if subscription_tier == 'free':
                st.markdown("""
                <div class="feature-card" style="border-left-color: #ffc107;">
                    <strong>💡 Cost Optimization Tip:</strong><br>
                    You're on the free plan. Consider upgrading to Pro for better value at higher usage levels.
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No cost data available yet. Start using the platform to see your cost analysis!")
        
        # Show potential costs for different plans
        st.markdown("#### 💡 Plan Comparison")
        
        plans_data = {
            'Plan': ['Free', 'Pro', 'Enterprise'],
            'Monthly Cost': ['$0', '$29', '$99'],
            'Tokens Included': ['10K', '100K', '1M'],
            'Cost per Extra Token': ['N/A', '$0.001', '$0.0005']
        }
        
        df_plans = pd.DataFrame(plans_data)
        st.table(df_plans)
    
    # Cost optimization suggestions
    st.markdown("#### 💡 Cost Optimization Suggestions")
    
    suggestions = []
    
    token_usage_pct = calculate_usage_percentage(
        usage_stats.get('total_tokens', 0),
        get_subscription_limits(user_data.get('subscription_tier', 'free'))['monthly_tokens']
    )
    
    if token_usage_pct > 90:
        suggestions.append("🔴 You're approaching your token limit. Consider upgrading your plan.")
    elif token_usage_pct > 70:
        suggestions.append("🟡 You're using 70%+ of your tokens. Monitor usage to avoid overages.")
    else:
        suggestions.append("🟢 Your token usage is within normal limits.")
    
    if usage_stats.get('total_requests', 0) > 1000:
        suggestions.append("💡 Consider batching API requests to reduce costs.")
    
    if user_data.get('subscription_tier') == 'free' and total_cost > 10:
        suggestions.append("💰 Upgrading to Pro could save money at your usage level.")
    
    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")

def show_activity_timeline(activity_logs: List[Dict]):
    """Show detailed activity timeline"""
    
    st.markdown("### 🔄 Activity Timeline")
    
    if activity_logs:
        # Activity summary
        activity_summary = generate_activity_summary(activity_logs)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_metric_card(
                "Total Activities",
                str(activity_summary['total_activities']),
                "All time"
            )
        
        with col2:
            create_metric_card(
                "Most Common",
                activity_summary['most_common_activity'].replace('_', ' ').title(),
                "Activity type"
            )
        
        with col3:
            recent_activity_time = time_ago(activity_logs[-1].get('created_at', '')) if activity_logs else 'Never'
            create_metric_card(
                "Last Activity",
                recent_activity_time,
                "Most recent"
            )
        
        # Activity timeline
        st.markdown("#### 📋 Recent Activities")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            activity_filter = st.selectbox(
                "Filter by Type",
                options=['All'] + list(set([log.get('activity_type', 'Unknown') for log in activity_logs]))
            )
        
        with col2:
            limit = st.selectbox(
                "Show Last",
                options=[10, 25, 50, 100],
                index=1
            )
        
        with col3:
            sort_order = st.selectbox(
                "Sort Order",
                options=['Newest First', 'Oldest First'],
                index=0
            )
        
        # Filter and sort activities
        filtered_logs = activity_logs
        
        if activity_filter != 'All':
            filtered_logs = [log for log in filtered_logs if log.get('activity_type') == activity_filter]
        
        if sort_order == 'Oldest First':
            filtered_logs = filtered_logs[::-1]
        
        filtered_logs = filtered_logs[:limit]
        
        # Display activities
        for i, activity in enumerate(filtered_logs):
            activity_time = safe_date_format(activity.get('created_at', ''), '%B %d, %Y at %I:%M %p')
            activity_type = activity.get('activity_type', 'Unknown').replace('_', ' ').title()
            description = activity.get('description', 'No description available')
            
            # Color coding based on activity type
            color_map = {
                'login': '#4caf50',
                'logout': '#ff9800',
                'profile_update': '#2196f3',
                'api_request': '#9c27b0',
                'file_upload': '#00bcd4',
                'chat_created': '#8bc34a',
                'error': '#f44336'
            }
            
            activity_color = color_map.get(activity.get('activity_type', ''), '#666')
            
            st.markdown(f"""
            <div class="dashboard-card" style="margin: 10px 0; padding: 15px; border-left: 4px solid {activity_color};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <strong style="color: {activity_color};">{activity_type}</strong>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;">{description}</p>
                        {f'<small style="color: #888;">Metadata: {activity.get("metadata", {})}</small>' if activity.get('metadata') else ''}
                    </div>
                    <div style="text-align: right; min-width: 150px;">
                        <small style="color: #888;">{activity_time}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(activity_logs) > limit:
            st.info(f"Showing {limit} of {len(activity_logs)} activities. Adjust the filter to see more.")
    
    else:
        st.info("No activity logs found. Start using the platform to see your activity timeline!")

def show_detailed_reports(user_data: Dict, usage_stats: Dict, activity_logs: List[Dict]):
    """Show detailed reports and export options"""
    
    st.markdown("### 📋 Detailed Reports")
    
    # Report generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Generate Reports")
        
        report_type = st.selectbox(
            "Report Type",
            options=[
                "Usage Summary",
                "Cost Analysis",
                "Activity Report",
                "Performance Metrics",
                "Security Report"
            ]
        )
        
        date_range = st.selectbox(
            "Date Range",
            options=[
                "Last 7 days",
                "Last 30 days",
                "Last 90 days",
                "This year",
                "All time"
            ],
            index=1
        )
        
        report_format = st.selectbox(
            "Format",
            options=["PDF", "CSV", "JSON", "Excel"]
        )
        
        if st.button("📥 Generate Report", use_container_width=True):
            st.info(f"Generating {report_type} report for {date_range} in {report_format} format...")
            # Report generation would be implemented here
    
    with col2:
        st.markdown("#### 📈 Quick Stats")
        
        # Calculate some quick statistics
        total_days_active = len(set([log.get('created_at', '')[:10] for log in activity_logs if log.get('created_at')]))
        avg_daily_tokens = usage_stats.get('total_tokens', 0) / max(total_days_active, 1)
        avg_daily_cost = usage_stats.get('total_cost', 0) / max(total_days_active, 1)
        
        st.markdown(f"""
        <div class="feature-card">
            <strong>📅 Active Days:</strong> {total_days_active}<br>
            <strong>🔢 Avg Daily Tokens:</strong> {avg_daily_tokens:.0f}<br>
            <strong>💰 Avg Daily Cost:</strong> {format_currency(avg_daily_cost)}<br>
            <strong>⚡ Efficiency Score:</strong> {min(100, int(usage_stats.get('total_tokens', 0) / max(usage_stats.get('total_cost', 0.01), 0.01)))}/100
        </div>
        """, unsafe_allow_html=True)
    
    # Data export section
    st.markdown("---")
    st.markdown("#### 📤 Data Export")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("📊 Export Usage Data", use_container_width=True):
            st.info("Usage data export would be generated here")
    
    with col4:
        if st.button("📋 Export Activity Logs", use_container_width=True):
            st.info("Activity logs export would be generated here")
    
    with col5:
        if st.button("💰 Export Cost Data", use_container_width=True):
            st.info("Cost data export would be generated here")
    
    # Privacy and data retention info
    st.markdown("---")
    st.markdown("#### 🔒 Privacy & Data Retention")
    
    st.markdown("""
    <div class="feature-card">
        <strong>Data Retention Policy:</strong><br>
        • Activity logs: 1 year<br>
        • Usage statistics: 2 years<br>
        • Cost data: 7 years (for tax purposes)<br>
        • Personal data: Until account deletion<br><br>
        
        <strong>Privacy:</strong><br>
        Your data is encrypted and never shared with third parties. 
        You can request data deletion at any time from your profile settings.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
