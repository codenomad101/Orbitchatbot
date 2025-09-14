#!/usr/bin/env python3
"""
Test script to debug login functionality
"""

import requests
import json

def test_backend_login():
    """Test backend login"""
    print("🔍 Testing Backend Login...")
    
    url = "http://localhost:8000/auth/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend Login Successful!")
            print(f"Token: {result['access_token'][:50]}...")
            print(f"User: {result['user']['username']} ({result['user']['role']})")
            return result
        else:
            print(f"❌ Backend Login Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_frontend():
    """Test frontend accessibility"""
    print("\n🔍 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:8050", timeout=10)
        print(f"Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print("❌ Frontend is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Frontend Error: {str(e)}")
        return False

def main():
    print("🧪 SKF Orbitbot Login Test")
    print("=" * 40)
    
    # Test backend
    backend_result = test_backend_login()
    
    # Test frontend
    frontend_result = test_frontend()
    
    print("\n📊 Summary:")
    print("-" * 20)
    
    if backend_result and frontend_result:
        print("✅ Both backend and frontend are working!")
        print("\n🔐 Try logging in with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🌐 Access: http://localhost:8050")
    else:
        print("❌ Some issues detected:")
        if not backend_result:
            print("   • Backend login failed")
        if not frontend_result:
            print("   • Frontend not accessible")

if __name__ == "__main__":
    main()


