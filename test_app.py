#!/usr/bin/env python3
"""
Test script for Mehndi App
Run this to verify the application setup
"""

import sys
import os
import sqlite3

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import streamlit as st
        import bcrypt
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database creation and connection"""
    try:
        # Import database module
        from database import init_database, get_db_connection

        # Initialize database
        if init_database():
            print("✅ Database initialized successfully")

            # Test connection
            conn = get_db_connection()
            if conn:
                conn.close()
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed")
                return False
        else:
            print("❌ Database initialization failed")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_auth():
    """Test authentication functions"""
    try:
        from auth import hash_password, verify_password, create_user

        # Test password hashing
        password = "test123"
        hashed = hash_password(password)

        if verify_password(password, hashed):
            print("✅ Password hashing and verification working")
        else:
            print("❌ Password verification failed")
            return False

        # Test user creation
        success = create_user("testuser", "testpass", "user")
        if success:
            print("✅ User creation successful")
            return True
        else:
            print("❌ User creation failed")
            return False
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False

def test_utils():
    """Test utility functions"""
    try:
        from utils import validate_email, validate_phone, format_price, get_greeting

        # Test email validation
        if validate_email("test@example.com"):
            print("✅ Email validation working")
        else:
            print("❌ Email validation failed")
            return False

        # Test phone validation
        if validate_phone("+1234567890"):
            print("✅ Phone validation working")
        else:
            print("❌ Phone validation failed")
            return False

        # Test price formatting
        formatted = format_price("500-1000")
        if formatted == "₹500 - ₹1000":
            print("✅ Price formatting working")
        else:
            print("❌ Price formatting failed")
            return False

        # Test greeting
        greeting = get_greeting()
        if greeting in ["Good morning", "Good afternoon", "Good evening", "Good night"]:
            print("✅ Greeting function working")
        else:
            print("❌ Greeting function failed")
            return False

        return True
    except Exception as e:
        print(f"❌ Utils test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Mehndi App Setup")
    print("=" * 40)

    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Authentication", test_auth),
        ("Utilities", test_utils)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! App is ready to run.")
        print("\n🚀 To start the app:")
        print("   streamlit run main.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 To install missing dependencies:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
