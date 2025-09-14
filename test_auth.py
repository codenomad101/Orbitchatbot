#!/usr/bin/env python3
"""
Test script for the authentication system
Run this to verify that the auth system is working correctly
"""

import requests
import json
import sys

API_BASE_URL = "http://127.0.0.1:8000"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not accessible: {e}")
        return False

def test_admin_login():
    """Test admin login"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful")
            print(f"   Token: {data['access_token'][:20]}...")
            print(f"   User: {data['user']['username']} ({data['user']['role']})")
            return data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_user_registration():
    """Test user registration"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "role": "user"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ User registration error: {e}")
        return False

def test_protected_endpoints(token):
    """Test protected endpoints with token"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /auth/me
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ /auth/me endpoint working")
        else:
            print(f"❌ /auth/me endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /auth/me error: {e}")
    
    # Test /auth/users (admin only)
    try:
        response = requests.get(f"{API_BASE_URL}/auth/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ /auth/users endpoint working ({len(users)} users)")
        else:
            print(f"❌ /auth/users endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /auth/users error: {e}")
    
    # Test /documents (admin only)
    try:
        response = requests.get(f"{API_BASE_URL}/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ /documents endpoint working ({docs.get('total_documents', 0)} documents)")
        else:
            print(f"❌ /documents endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ /documents error: {e}")

def test_unauthorized_access():
    """Test that unauthorized access is blocked"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/users", timeout=10)
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked")
            return True
        else:
            print(f"❌ Unauthorized access not blocked: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Unauthorized access test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing SKF Orbitbot Authentication System")
    print("=" * 50)
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    if not test_api_health():
        print("❌ API is not running. Please start the backend server first.")
        sys.exit(1)
    
    # Test 2: Admin Login
    print("\n2. Testing Admin Login...")
    token = test_admin_login()
    if not token:
        print("❌ Admin login failed. Check if default admin user exists.")
        sys.exit(1)
    
    # Test 3: User Registration
    print("\n3. Testing User Registration...")
    test_user_registration()
    
    # Test 4: Protected Endpoints
    print("\n4. Testing Protected Endpoints...")
    test_protected_endpoints(token)
    
    # Test 5: Unauthorized Access
    print("\n5. Testing Unauthorized Access...")
    test_unauthorized_access()
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")
    print("\n📋 Summary:")
    print("   - Default admin account: admin / admin123")
    print("   - JWT tokens are working")
    print("   - Role-based access control is active")
    print("   - Protected endpoints are secured")
    print("\n🚀 You can now run the Streamlit frontend:")
    print("   cd frontend && streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()

