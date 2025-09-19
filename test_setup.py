#!/usr/bin/env python3
"""
Enhanced Streamlit User Management System - Setup Validation Script
Tests all components to ensure proper setup and functionality
"""

import sys
import os
import importlib
from typing import List, Tuple, Dict
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all required imports"""
    results = []
    
    # Core dependencies
    dependencies = [
        ('streamlit', 'Streamlit framework'),
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
        ('plotly.express', 'Data visualization'),
        ('plotly.graph_objects', 'Advanced plotting'),
        ('datetime', 'Date/time handling'),
        ('typing', 'Type hints'),
        ('os', 'Operating system interface'),
        ('sys', 'System-specific parameters'),
        ('re', 'Regular expressions'),
        ('hashlib', 'Secure hashing'),
        ('uuid', 'UUID generation'),
        ('json', 'JSON handling'),
    ]
    
    # Optional dependencies
    optional_dependencies = [
        ('supabase', 'Supabase client'),
        ('bcrypt', 'Password hashing'),
        ('cryptography', 'Cryptographic functions'),
        ('email_validator', 'Email validation'),
        ('python_dateutil', 'Date utilities'),
        ('requests', 'HTTP requests'),
    ]
    
    print("🔍 Testing Core Dependencies...")
    for module, description in dependencies:
        try:
            importlib.import_module(module)
            results.append((module, True, f"✅ {description}"))
        except ImportError as e:
            results.append((module, False, f"❌ {description} - {str(e)}"))
    
    print("\n🔍 Testing Optional Dependencies...")
    for module, description in optional_dependencies:
        try:
            importlib.import_module(module)
            results.append((module, True, f"✅ {description}"))
        except ImportError as e:
            results.append((module, False, f"⚠️  {description} - {str(e)} (Optional)"))
    
    return results

def test_components() -> List[Tuple[str, bool, str]]:
    """Test application components"""
    results = []
    
    components = [
        ('components.auth', 'Authentication Manager'),
        ('components.database', 'Database Manager'),
        ('components.ui_components', 'UI Components'),
        ('components.utils', 'Utility Functions'),
        ('config.settings', 'Application Settings'),
    ]
    
    print("\n🧩 Testing Application Components...")
    for module, description in components:
        try:
            mod = importlib.import_module(module)
            
            # Test specific classes/functions exist
            if module == 'components.auth':
                assert hasattr(mod, 'AuthManager'), "AuthManager class not found"
            elif module == 'components.database':
                assert hasattr(mod, 'DatabaseManager'), "DatabaseManager class not found"
            elif module == 'components.ui_components':
                assert hasattr(mod, 'load_custom_css'), "load_custom_css function not found"
            elif module == 'components.utils':
                assert hasattr(mod, 'format_currency'), "format_currency function not found"
            elif module == 'config.settings':
                assert hasattr(mod, 'AppSettings'), "AppSettings class not found"
                assert hasattr(mod, 'settings'), "settings instance not found"
            
            results.append((module, True, f"✅ {description}"))
        except Exception as e:
            results.append((module, False, f"❌ {description} - {str(e)}"))
    
    return results

def test_file_structure() -> List[Tuple[str, bool, str]]:
    """Test required file structure"""
    results = []
    
    required_files = [
        ('main.py', 'Main application file'),
        ('requirements.txt', 'Dependencies file'),
        ('README.md', 'Documentation'),
        ('.env.example', 'Environment template'),
        ('.streamlit/config.toml', 'Streamlit configuration'),
        ('assets/styles.css', 'Custom styling'),
        ('config/settings.py', 'Application settings'),
        ('components/__init__.py', 'Components package'),
        ('components/auth.py', 'Authentication component'),
        ('components/database.py', 'Database component'),
        ('components/ui_components.py', 'UI components'),
        ('components/utils.py', 'Utilities component'),
    ]
    
    required_pages = [
        ('pages/01_🏠_User_Dashboard.py', 'User Dashboard'),
        ('pages/02_👤_Profile_Settings.py', 'Profile Settings'),
        ('pages/03_📊_Usage_Analytics.py', 'Usage Analytics'),
        ('pages/04_🔧_Admin_Panel.py', 'Admin Panel'),
        ('pages/05_👥_User_Management.py', 'User Management'),
    ]
    
    print("\n📁 Testing File Structure...")
    
    all_files = required_files + required_pages
    
    for file_path, description in all_files:
        if os.path.exists(file_path):
            results.append((file_path, True, f"✅ {description}"))
        else:
            results.append((file_path, False, f"❌ {description} - File not found"))
    
    return results

def test_configuration() -> List[Tuple[str, bool, str]]:
    """Test configuration setup"""
    results = []
    
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config.settings import settings
        
        # Test basic configuration
        config_tests = [
            (hasattr(settings, 'APP_NAME'), 'APP_NAME setting'),
            (hasattr(settings, 'APP_VERSION'), 'APP_VERSION setting'),
            (hasattr(settings, 'get_subscription_limits'), 'Subscription limits method'),
            (hasattr(settings, 'get_role_permissions'), 'Role permissions method'),
            (hasattr(settings, 'validate_config'), 'Config validation method'),
        ]
        
        for test_result, description in config_tests:
            if test_result:
                results.append((description, True, f"✅ {description}"))
            else:
                results.append((description, False, f"❌ {description} - Not found"))
        
        # Test configuration methods
        try:
            limits = settings.get_subscription_limits()
            assert isinstance(limits, dict), "Subscription limits should be a dict"
            assert 'free' in limits, "Free tier should be defined"
            results.append(('subscription_limits', True, "✅ Subscription limits configuration"))
        except Exception as e:
            results.append(('subscription_limits', False, f"❌ Subscription limits - {str(e)}"))
        
        try:
            permissions = settings.get_role_permissions()
            assert isinstance(permissions, dict), "Role permissions should be a dict"
            assert 'user' in permissions, "User role should be defined"
            assert 'admin' in permissions, "Admin role should be defined"
            results.append(('role_permissions', True, "✅ Role permissions configuration"))
        except Exception as e:
            results.append(('role_permissions', False, f"❌ Role permissions - {str(e)}"))
        
    except Exception as e:
        results.append(('settings_import', False, f"❌ Settings import failed - {str(e)}"))
    
    return results

def test_environment() -> List[Tuple[str, bool, str]]:
    """Test environment setup"""
    results = []
    
    print("\n🌍 Testing Environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        results.append(('python_version', True, f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"))
    else:
        results.append(('python_version', False, f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires 3.11+"))
    
    # Check environment file
    if os.path.exists('.env'):
        results.append(('.env', True, "✅ Environment file exists"))
    else:
        results.append(('.env', False, "⚠️  Environment file not found - Copy from .env.example"))
    
    # Check critical environment variables (if .env exists)
    if os.path.exists('.env'):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            critical_vars = [
                'SUPABASE_URL',
                'SUPABASE_ANON_KEY',
                'SUPABASE_SERVICE_ROLE_KEY'
            ]
            
            for var in critical_vars:
                if os.getenv(var):
                    results.append((var, True, f"✅ {var} configured"))
                else:
                    results.append((var, False, f"❌ {var} not configured"))
        except ImportError:
            results.append(('dotenv', False, "⚠️  python-dotenv not installed (optional)"))
    
    return results

def test_pages() -> List[Tuple[str, bool, str]]:
    """Test page imports and basic structure"""
    results = []
    
    print("\n📄 Testing Page Modules...")
    
    pages = [
        'pages.01_🏠_User_Dashboard',
        'pages.02_👤_Profile_Settings', 
        'pages.03_📊_Usage_Analytics',
        'pages.04_🔧_Admin_Panel',
        'pages.05_👥_User_Management'
    ]
    
    for page in pages:
        try:
            # Convert file path to module path
            module_name = page.replace('/', '.').replace('.py', '')
            
            # Try to import the module
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                results.append((page, True, f"✅ {page.split('.')[-1]} page"))
            else:
                results.append((page, False, f"❌ {page.split('.')[-1]} page - Module not found"))
        except Exception as e:
            results.append((page, False, f"❌ {page.split('.')[-1]} page - {str(e)}"))
    
    return results

def run_all_tests() -> Dict[str, List[Tuple[str, bool, str]]]:
    """Run all tests and return results"""
    
    print("🚀 Enhanced Streamlit User Management System - Setup Validation")
    print("=" * 70)
    
    test_results = {
        'imports': test_imports(),
        'components': test_components(),
        'file_structure': test_file_structure(),
        'configuration': test_configuration(),
        'environment': test_environment(),
        'pages': test_pages()
    }
    
    return test_results

def print_summary(test_results: Dict[str, List[Tuple[str, bool, str]]]):
    """Print test summary"""
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0
    
    for category, results in test_results.items():
        category_passed = sum(1 for _, success, _ in results if success)
        category_total = len(results)
        category_failed = category_total - category_passed
        category_warnings = sum(1 for _, _, msg in results if "⚠️" in msg)
        
        total_tests += category_total
        passed_tests += category_passed
        failed_tests += category_failed
        warnings += category_warnings
        
        status_icon = "✅" if category_failed == 0 else "❌"
        print(f"{status_icon} {category.upper()}: {category_passed}/{category_total} passed")
        
        # Show failed tests
        for name, success, message in results:
            if not success and "⚠️" not in message:
                print(f"   ❌ {message}")
            elif "⚠️" in message:
                print(f"   ⚠️  {message}")
    
    print("\n" + "-" * 70)
    print(f"📈 OVERALL RESULTS:")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   ⚠️  Warnings: {warnings}")
    print(f"   📊 Total: {total_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"   🎯 Success Rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All critical tests passed! Your application is ready to run.")
        print("   Run: streamlit run main.py")
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Please address the issues above before running the application.")
        print("\n💡 Common fixes:")
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Copy environment file: cp .env.example .env")
        print("   • Configure Supabase credentials in .env")
        print("   • Ensure all files are in the correct locations")

def main():
    """Main test execution"""
    try:
        test_results = run_all_tests()
        print_summary(test_results)
        
        # Return appropriate exit code
        failed_count = sum(
            sum(1 for _, success, msg in results if not success and "⚠️" not in msg)
            for results in test_results.values()
        )
        
        sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
