import streamlit as st
import re
import hashlib
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength and return validation results"""
    result = {
        'valid': True,
        'errors': [],
        'strength': 'weak'
    }
    
    if len(password) < 6:
        result['valid'] = False
        result['errors'].append('Password must be at least 6 characters long')
    
    if len(password) < 8:
        result['errors'].append('Consider using at least 8 characters for better security')
    
    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        result['errors'].append('Consider adding uppercase letters')
    
    # Check for lowercase
    if not re.search(r'[a-z]', password):
        result['errors'].append('Consider adding lowercase letters')
    
    # Check for numbers
    if not re.search(r'\d', password):
        result['errors'].append('Consider adding numbers')
    
    # Check for special characters
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['errors'].append('Consider adding special characters')
    
    # Determine strength
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score >= 4:
        result['strength'] = 'strong'
    elif score >= 2:
        result['strength'] = 'medium'
    
    return result

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def calculate_usage_percentage(used: int, limit: int) -> float:
    """Calculate usage percentage"""
    if limit == 0:
        return 0.0
    return min((used / limit) * 100, 100.0)

def get_subscription_limits(tier: str) -> Dict[str, int]:
    """Get subscription limits based on tier"""
    limits = {
        'free': {
            'monthly_tokens': 10000,
            'max_files': 5,
            'max_threads': 10,
            'max_assistants': 2
        },
        'pro': {
            'monthly_tokens': 100000,
            'max_files': 50,
            'max_threads': 100,
            'max_assistants': 10
        },
        'enterprise': {
            'monthly_tokens': 1000000,
            'max_files': 500,
            'max_threads': 1000,
            'max_assistants': 50
        }
    }
    
    return limits.get(tier, limits['free'])

def time_ago(date_string: str) -> str:
    """Convert date string to human readable time ago format"""
    if not date_string:
        return "Never"
    
    try:
        if 'T' in date_string:
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            date_obj = datetime.fromisoformat(date_string)
        else:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        
        now = datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()
        diff = now - date_obj
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 2592000:  # 30 days
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 31536000:  # 365 days
            months = int(seconds // 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds // 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"
            
    except Exception:
        return "Unknown"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def parse_json_safely(json_string: str) -> Dict:
    """Safely parse JSON string"""
    try:
        return json.loads(json_string) if json_string else {}
    except (json.JSONDecodeError, TypeError):
        return {}

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:.2f}"

def get_role_color(role: str) -> str:
    """Get color for user role"""
    colors = {
        'admin': '#ff9800',
        'moderator': '#9c27b0',
        'user': '#4caf50',
        'premium': '#ffc107'
    }
    return colors.get(role.lower(), '#4caf50')

def get_status_color(status: str) -> str:
    """Get color for status"""
    colors = {
        'active': '#4caf50',
        'inactive': '#f44336',
        'pending': '#ff9800',
        'approved': '#4caf50',
        'rejected': '#f44336',
        'suspended': '#f44336'
    }
    return colors.get(status.lower(), '#666')

def generate_activity_summary(activities: List[Dict]) -> Dict:
    """Generate activity summary from activity logs"""
    if not activities:
        return {
            'total_activities': 0,
            'recent_activity': 'No recent activity',
            'most_common_activity': 'None',
            'activity_types': {}
        }
    
    # Count activity types
    activity_types = {}
    for activity in activities:
        activity_type = activity.get('activity_type', 'unknown')
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
    
    # Find most common activity
    most_common = max(activity_types.items(), key=lambda x: x[1])[0] if activity_types else 'None'
    
    # Get most recent activity
    recent_activity = activities[-1].get('description', 'No description') if activities else 'No recent activity'
    
    return {
        'total_activities': len(activities),
        'recent_activity': recent_activity,
        'most_common_activity': most_common,
        'activity_types': activity_types
    }

def filter_users(users: List[Dict], filters: Dict) -> List[Dict]:
    """Filter users based on provided filters"""
    filtered = users
    
    # Role filter
    if filters.get('role') and filters['role'] != 'All':
        filtered = [u for u in filtered if u.get('role') == filters['role']]
    
    # Status filter
    if filters.get('status') and filters['status'] != 'All':
        if filters['status'] == 'Active':
            filtered = [u for u in filtered if u.get('is_active', True)]
        elif filters['status'] == 'Inactive':
            filtered = [u for u in filtered if not u.get('is_active', True)]
    
    # Subscription tier filter
    if filters.get('subscription_tier') and filters['subscription_tier'] != 'All':
        filtered = [u for u in filtered if u.get('subscription_tier') == filters['subscription_tier']]
    
    # Search term filter
    if filters.get('search_term'):
        search_term = filters['search_term'].lower()
        filtered = [u for u in filtered 
                   if search_term in u.get('email', '').lower() 
                   or search_term in u.get('full_name', '').lower()
                   or search_term in u.get('username', '').lower()]
    
    return filtered

def paginate_data(data: List, page: int, items_per_page: int = 10) -> Dict:
    """Paginate data and return pagination info"""
    total_items = len(data)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    return {
        'data': data[start_idx:end_idx],
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'items_per_page': items_per_page,
        'start_idx': start_idx,
        'end_idx': min(end_idx, total_items)
    }

def export_data_to_csv(data: List[Dict], filename: str) -> str:
    """Export data to CSV format"""
    import pandas as pd
    import io
    
    if not data:
        return ""
    
    df = pd.DataFrame(data)
    
    # Convert to CSV string
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def log_user_action(user_id: str, action: str, details: str = "", metadata: Dict = None):
    """Log user action (helper function)"""
    try:
        from .database import DatabaseManager
        
        db = DatabaseManager(use_service_role=True)
        db.log_user_activity(
            user_id=user_id,
            activity_type=action,
            description=details,
            metadata=metadata or {}
        )
    except Exception:
        # Silently fail for logging
        pass

def check_rate_limit(user_id: str, action: str, limit: int = 10, window_minutes: int = 60) -> bool:
    """Check if user has exceeded rate limit for an action"""
    # This is a simplified rate limiting check
    # In production, you'd want to use Redis or similar
    
    rate_limit_key = f"rate_limit_{user_id}_{action}"
    
    if rate_limit_key not in st.session_state:
        st.session_state[rate_limit_key] = {
            'count': 0,
            'window_start': datetime.now()
        }
    
    rate_data = st.session_state[rate_limit_key]
    
    # Check if window has expired
    if datetime.now() - rate_data['window_start'] > timedelta(minutes=window_minutes):
        rate_data['count'] = 0
        rate_data['window_start'] = datetime.now()
    
    # Check if limit exceeded
    if rate_data['count'] >= limit:
        return False
    
    # Increment counter
    rate_data['count'] += 1
    return True

def get_user_avatar_url(user: Dict) -> str:
    """Get user avatar URL or generate a default one"""
    avatar_url = user.get('avatar_url')
    
    if avatar_url:
        return avatar_url
    
    # Generate a default avatar based on user's name or email
    name = user.get('full_name', user.get('email', 'User'))
    initials = ''.join([word[0].upper() for word in name.split()[:2]])
    
    # Use a service like UI Avatars or generate a simple colored background
    return f"https://ui-avatars.com/api/?name={initials}&background=4caf50&color=fff&size=128"

def calculate_user_score(user: Dict) -> int:
    """Calculate a user engagement score"""
    score = 0
    
    # Activity score
    if user.get('activity_logs_count', 0) > 0:
        score += min(user['activity_logs_count'] * 2, 50)
    
    # Usage score
    if user.get('tokens_used', 0) > 0:
        score += min(user['tokens_used'] // 1000, 30)
    
    # Content creation score
    score += user.get('chat_threads_count', 0) * 5
    score += user.get('file_uploads_count', 0) * 3
    score += user.get('custom_assistants_count', 0) * 10
    
    # Subscription bonus
    if user.get('subscription_tier') == 'pro':
        score += 20
    elif user.get('subscription_tier') == 'enterprise':
        score += 50
    
    return min(score, 100)  # Cap at 100
