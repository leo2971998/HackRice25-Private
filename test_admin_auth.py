#!/usr/bin/env python3
"""
Test script for admin authentication functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_admin_registration_and_login():
    """Test admin account creation and authentication"""
    print("Testing Admin Authentication System")
    print("=" * 50)
    
    # Test data
    admin_email = f"admin_test_{int(time.time())}@example.com"
    user_email = f"user_test_{int(time.time())}@example.com"
    password = "testpassword123"
    
    session = requests.Session()
    
    try:
        # Test 1: Register admin account
        print("1. Testing admin registration...")
        admin_data = {
            "email": admin_email,
            "password": password,
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }
        
        response = session.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 200:
            print("✅ Admin registration successful")
        else:
            print(f"❌ Admin registration failed: {response.text}")
            return False
            
        # Test 2: Register regular user
        print("2. Testing regular user registration...")
        user_data = {
            "email": user_email,
            "password": password,
            "first_name": "Regular",
            "last_name": "User",
            "role": "user"
        }
        
        response = session.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print("✅ User registration successful")
        else:
            print(f"❌ User registration failed: {response.text}")
            return False
            
        # Test 3: Login as admin and check access
        print("3. Testing admin login and access...")
        login_data = {"email": admin_email, "password": password}
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            if login_result.get("role") == "admin":
                print("✅ Admin login successful with correct role")
            else:
                print(f"❌ Admin login role mismatch: {login_result}")
                return False
        else:
            print(f"❌ Admin login failed: {response.text}")
            return False
            
        # Test 4: Check admin /me endpoint
        print("4. Testing admin /me endpoint...")
        response = session.get(f"{BASE_URL}/me")
        if response.status_code == 200:
            user_info = response.json()
            if user_info.get("role") == "admin":
                print("✅ Admin /me endpoint returns correct role")
            else:
                print(f"❌ Admin /me role mismatch: {user_info}")
                return False
        else:
            print(f"❌ Admin /me failed: {response.text}")
            return False
            
        # Test 5: Test admin-only endpoint access
        print("5. Testing admin-only endpoint access...")
        response = session.get(f"{BASE_URL}/admin/status")
        if response.status_code == 200:
            print("✅ Admin can access admin-only endpoints")
        else:
            print(f"❌ Admin cannot access admin endpoints: {response.text}")
            return False
            
        # Test 6: Login as regular user and test admin access denial
        print("6. Testing regular user admin access denial...")
        login_data = {"email": user_email, "password": password}
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ Regular user login successful")
        else:
            print(f"❌ Regular user login failed: {response.text}")
            return False
            
        # Test 7: Check that regular user cannot access admin endpoints
        print("7. Testing admin endpoint protection...")
        response = session.get(f"{BASE_URL}/admin/status")
        if response.status_code == 403:
            print("✅ Regular user correctly denied admin access")
        else:
            print(f"❌ Regular user inappropriately allowed admin access: {response.status_code}")
            return False
            
        print("\n🎉 All tests passed! Admin authentication is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_admin_registration_and_login()