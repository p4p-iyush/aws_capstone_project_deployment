#!/usr/bin/env python3
"""
Installation Test Script
Verifies that all components are properly installed
"""

import sys
import os

def test_python_version():
    """Check Python version"""
    print("Testing Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def test_imports():
    """Test critical imports"""
    imports = [
        ('flask', 'Flask'),
        ('boto3', 'boto3'),
        ('bcrypt', 'bcrypt'),
        ('flask_session', 'Flask-Session'),
    ]
    
    all_passed = True
    for module, name in imports:
        print(f"Testing {name}...", end=" ")
        try:
            __import__(module)
            print("✓")
        except ImportError:
            print("✗ Not installed")
            all_passed = False
    
    return all_passed

def test_directory_structure():
    """Check if all directories exist"""
    print("\nTesting directory structure...", end=" ")
    required_dirs = [
        'app',
        'app/models',
        'app/services',
        'app/routes',
        'app/templates',
        'app/static',
        'aws',
        'docs'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if not os.path.isdir(directory):
            print(f"\n  ✗ Missing: {directory}")
            all_exist = False
    
    if all_exist:
        print("✓")
    
    return all_exist

def test_required_files():
    """Check if critical files exist"""
    print("Testing required files...", end=" ")
    required_files = [
        'run.py',
        'requirements.txt',
        '.env.example',
        'app/__init__.py',
        'app/config.py',
    ]
    
    all_exist = True
    for file in required_files:
        if not os.path.isfile(file):
            print(f"\n  ✗ Missing: {file}")
            all_exist = False
    
    if all_exist:
        print("✓")
    
    return all_exist

def test_env_file():
    """Check if .env file exists"""
    print("Testing environment configuration...", end=" ")
    if os.path.isfile('.env'):
        print("✓ .env file exists")
        return True
    elif os.path.isfile('.env.example'):
        print("⚠️  .env not found (use .env.example)")
        return True
    else:
        print("✗ No configuration file")
        return False

def test_app_imports():
    """Test if app can be imported"""
    print("Testing Flask app...", end=" ")
    try:
        sys.path.insert(0, os.getcwd())
        from app import create_app
        app = create_app('development')
        print("✓")
        return True
    except Exception as e:
        print(f"✗ {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Banking System - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Python Packages", test_imports()))
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Required Files", test_required_files()))
    results.append(("Environment Config", test_env_file()))
    results.append(("Flask Application", test_app_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("\nNext steps:")
        print("1. Configure AWS credentials (aws configure)")
        print("2. Create DynamoDB tables (python3 aws/dynamodb_setup.py)")
        print("3. Run application (python3 run.py)")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
