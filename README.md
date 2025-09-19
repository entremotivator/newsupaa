# Enhanced Streamlit User Management System

A comprehensive, production-ready user management system built with Streamlit, featuring role-based authentication, admin panels, user analytics, and modern UI/UX design.

## 🚀 Features

### 🔐 Authentication & Security
- **User Registration & Login** - Secure signup/signin with email verification
- **Role-Based Access Control** - User, Moderator, and Admin roles with granular permissions
- **Session Management** - Secure session handling with configurable timeouts
- **Password Security** - Bcrypt hashing with customizable strength requirements
- **Two-Factor Authentication** - Optional 2FA for enhanced security
- **Account Approval Workflow** - Optional admin approval for new registrations

### 👥 User Management
- **Comprehensive User Profiles** - Detailed user information and preferences
- **Admin User Management** - Full CRUD operations for user accounts
- **Bulk Operations** - Batch processing for multiple users
- **User Analytics** - Detailed usage statistics and activity tracking
- **Pending Approvals** - Streamlined approval workflow for new users
- **Activity Logging** - Comprehensive audit trail of user actions

### 📊 Analytics & Reporting
- **Usage Analytics** - Token usage, API requests, and cost analysis
- **User Activity Tracking** - Login patterns, feature usage, and engagement metrics
- **System Statistics** - Platform-wide metrics and performance indicators
- **Revenue Analytics** - Subscription tier analysis and revenue tracking
- **Export Capabilities** - CSV/PDF export for reports and user data

### 🎨 Modern UI/UX
- **Responsive Design** - Mobile-friendly interface with adaptive layouts
- **Light Green Theme** - Professional, accessible color scheme
- **Interactive Components** - Hover effects, animations, and micro-interactions
- **Dashboard Cards** - Information-rich, visually appealing data presentation
- **Progress Indicators** - Visual feedback for usage limits and quotas
- **Accessibility Features** - WCAG compliant with keyboard navigation support

### ⚙️ Admin Features
- **System Overview** - Real-time system health and key metrics
- **User Management Panel** - Advanced user administration tools
- **Notification System** - Broadcast messages to users and groups
- **System Settings** - Configurable application parameters
- **Maintenance Tools** - Database operations and system maintenance
- **Security Monitoring** - Failed login tracking and security alerts

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.28+
- **Backend**: Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + Custom Session Management
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Styling**: Custom CSS with modern design principles
- **Data Processing**: Pandas, NumPy

## 📋 Prerequisites

- Python 3.11 or higher
- Supabase account and project
- Git (for version control)
- Modern web browser

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd enhanced_streamlit_app
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 5. Set Up Supabase Database

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Copy your project URL and API keys to `.env`
3. Run the database setup script:

```sql
-- Create users table (if not exists)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    subscription_tier VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    email_confirmed_at TIMESTAMP,
    pending_approval BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_sign_in_at TIMESTAMP,
    website VARCHAR(255),
    tokens_used INTEGER DEFAULT 0,
    total_cost DECIMAL(10,2) DEFAULT 0.00,
    api_requests INTEGER DEFAULT 0,
    chat_threads_count INTEGER DEFAULT 0,
    file_uploads_count INTEGER DEFAULT 0,
    custom_assistants_count INTEGER DEFAULT 0,
    activity_logs_count INTEGER DEFAULT 0,
    voice_enabled BOOLEAN DEFAULT false,
    advanced_features BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    failed_login_attempts INTEGER DEFAULT 0
);

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);
```

### 6. Run the Application

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

## 📁 Project Structure

```
enhanced_streamlit_app/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── .env.example              # Environment configuration template
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── assets/
│   └── styles.css            # Custom CSS styling
├── components/
│   ├── __init__.py
│   ├── auth.py               # Authentication manager
│   ├── database.py           # Database operations
│   ├── ui_components.py      # Reusable UI components
│   └── utils.py              # Utility functions
├── config/
│   └── settings.py           # Application settings
└── pages/
    ├── 01_🏠_User_Dashboard.py      # User dashboard
    ├── 02_👤_Profile_Settings.py    # Profile management
    ├── 03_📊_Usage_Analytics.py     # Usage analytics
    ├── 04_🔧_Admin_Panel.py         # Admin panel
    └── 05_👥_User_Management.py     # User management
```

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Authentication
SESSION_TIMEOUT_HOURS=24
PASSWORD_MIN_LENGTH=8
REQUIRE_EMAIL_VERIFICATION=true
REQUIRE_ADMIN_APPROVAL=false

# Features
ENABLE_USER_REGISTRATION=true
ENABLE_2FA=true
ENABLE_ANALYTICS=true
MAINTENANCE_MODE=false

# UI/UX
THEME_PRIMARY_COLOR=#4caf50
ITEMS_PER_PAGE=10
```

### Subscription Tiers

Configure limits for different subscription tiers:

- **Free**: 10K tokens/month, 5 files, 10 threads
- **Pro**: 100K tokens/month, 50 files, 100 threads  
- **Enterprise**: 1M tokens/month, 500 files, 1000 threads

## 👤 User Roles & Permissions

### User Role
- View dashboard and personal analytics
- Edit profile and settings
- Use API within subscription limits
- Upload files and create chat threads

### Moderator Role
- All user permissions
- Moderate user content
- View user reports
- Manage user-generated content

### Admin Role
- All moderator permissions
- Full user management (CRUD operations)
- System administration and settings
- Bulk operations and notifications
- View system logs and analytics
- Manage subscriptions and approvals

## 🔧 Development

### Adding New Features

1. **New Pages**: Add to `pages/` directory with naming convention `NN_🔸_Page_Name.py`
2. **Components**: Add reusable components to `components/`
3. **Styling**: Update `assets/styles.css` for custom styling
4. **Configuration**: Add settings to `config/settings.py`

### Database Schema

The application uses the existing SQL structure with these main tables:
- `users` - User accounts and profiles
- `activity_logs` - User activity tracking

### Testing

```bash
# Run basic functionality tests
python -m pytest tests/ -v

# Test specific components
python -c "from components.auth import AuthManager; print('Auth module OK')"
python -c "from components.database import DatabaseManager; print('Database module OK')"
```

## 🚀 Deployment

### Local Development

```bash
streamlit run main.py --server.port 8501
```

### Production Deployment

1. **Environment Setup**:
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export SECURE_COOKIES=true
   ```

2. **Database Migration**:
   - Ensure all tables are created
   - Set up proper indexes
   - Configure backup strategy

3. **Security Checklist**:
   - [ ] Change default passwords
   - [ ] Enable HTTPS
   - [ ] Set secure cookie flags
   - [ ] Configure CORS properly
   - [ ] Enable audit logging
   - [ ] Set up monitoring

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📊 Monitoring & Analytics

### Built-in Analytics
- User registration trends
- Activity patterns and engagement
- Feature adoption rates
- Revenue and subscription metrics
- System performance indicators

### Health Checks
- Database connectivity
- API endpoint status
- File storage availability
- Email service status
- Background job processing

## 🔒 Security Features

- **Password Hashing**: Bcrypt with configurable rounds
- **Session Security**: Secure session tokens with expiration
- **Rate Limiting**: Configurable API and token rate limits
- **Input Validation**: Comprehensive input sanitization
- **CSRF Protection**: Built-in CSRF token validation
- **Audit Logging**: Complete activity audit trail
- **Failed Login Protection**: Account lockout after failed attempts

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify Supabase credentials in `.env`
   - Check network connectivity
   - Ensure database is accessible

2. **Authentication Issues**:
   - Clear browser cache and cookies
   - Check session timeout settings
   - Verify user account status

3. **Permission Errors**:
   - Confirm user role assignments
   - Check role-based access configuration
   - Verify admin account setup

4. **Styling Issues**:
   - Clear Streamlit cache: `streamlit cache clear`
   - Check CSS file loading
   - Verify theme configuration

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
streamlit run main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Submit a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and modular
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration documentation

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced reporting dashboard
- [ ] API rate limiting dashboard
- [ ] Multi-language support
- [ ] Advanced user segmentation
- [ ] Integration with external services
- [ ] Mobile app companion
- [ ] Advanced analytics and ML insights
- [ ] Automated user onboarding flows

### Performance Improvements
- [ ] Database query optimization
- [ ] Caching layer implementation
- [ ] Async processing for bulk operations
- [ ] CDN integration for static assets

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Minimum Python Version**: 3.11+
