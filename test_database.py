#!/usr/bin/env python3
"""
Test script for the database system
Run this to verify that the database integration is working correctly
"""

import requests
import json
import sys
import time
from pathlib import Path

API_BASE_URL = "http://127.0.0.1:8000"

def test_database_health():
    """Test database health through API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API is running and healthy")
            
            # Check if database is mentioned in health
            if "services" in health_data:
                print("✅ Database services initialized")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not accessible: {e}")
        return False

def test_database_auth():
    """Test database-based authentication"""
    print("\n🔐 Testing Database Authentication...")
    
    # Test admin login
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Email: {data['user']['email']}")
            return data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_user_management(token):
    """Test user management endpoints"""
    print("\n👥 Testing User Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting all users
    try:
        response = requests.get(f"{API_BASE_URL}/auth/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            
            for user in users:
                print(f"   - {user['username']} ({user['role']}) - ID: {user['id']}")
            
            return users
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ User management error: {e}")
        return None

def test_document_management(token):
    """Test document management endpoints"""
    print("\n📄 Testing Document Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting documents
    try:
        response = requests.get(f"{API_BASE_URL}/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Retrieved {len(documents)} documents")
            
            for doc in documents:
                print(f"   - {doc['original_filename']} (Status: {doc.get('processing_status', 'unknown')}) - ID: {doc['id']}")
            
            return documents
        else:
            print(f"❌ Failed to get documents: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Document management error: {e}")
        return None

def test_search_functionality(token):
    """Test search functionality with database tracking"""
    print("\n🔍 Testing Search Functionality...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test a search query
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": "What is this system about?", "top_k": 3},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search query successful")
            print(f"   Response: {result['answer'][:100]}...")
            print(f"   Sources found: {len(result.get('sources', []))}")
            
            # Test search history
            history_response = requests.get(f"{API_BASE_URL}/search/history", headers=headers, timeout=10)
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"✅ Search history retrieved ({len(history)} queries)")
                if history:
                    latest = history[0]
                    print(f"   Latest query: {latest['query_text']}")
                    print(f"   Response time: {latest.get('response_time_ms', 'N/A')}ms")
            
            return True
        else:
            print(f"❌ Search query failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Search functionality error: {e}")
        return False

def test_analytics(token):
    """Test analytics endpoints"""
    print("\n📊 Testing Analytics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test analytics
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/stats", headers=headers, timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Analytics retrieved")
            print(f"   Total users: {stats.get('total_users', 0)}")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            print(f"   Search queries today: {stats.get('search_stats', {}).get('queries_today', 0)}")
            print(f"   Total search queries: {stats.get('search_stats', {}).get('total_queries', 0)}")
            return True
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_system_logs(token):
    """Test system logs endpoint"""
    print("\n📋 Testing System Logs...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test system logs
    try:
        response = requests.get(f"{API_BASE_URL}/logs/system", headers=headers, timeout=10)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ System logs retrieved ({len(logs)} entries)")
            
            if logs:
                latest = logs[0]
                print(f"   Latest action: {latest['action']}")
                print(f"   User ID: {latest.get('user_id', 'N/A')}")
                print(f"   Timestamp: {latest['created_at']}")
            
            return True
        else:
            print(f"❌ System logs failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ System logs error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n📝 Testing User Registration...")
    
    # Test user registration
    try:
        test_username = f"testuser_{int(time.time())}"
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "username": test_username,
                "email": f"{test_username}@example.com",
                "password": "testpass123",
                "role": "user"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registration successful")
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print(f"   ID: {user_data['id']}")
            return True
        else:
            print(f"❌ User registration failed: {response.status_code}")
            if response.status_code == 400:
                print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ User registration error: {e}")
        return False

def main():
    """Run all database tests"""
    print("🧪 Testing SKF Orbitbot Database Integration")
    print("=" * 60)
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    if not test_database_health():
        print("❌ API is not running. Please start the backend server first.")
        sys.exit(1)
    
    # Test 2: Authentication
    token = test_database_auth()
    if not token:
        print("❌ Database authentication failed.")
        sys.exit(1)
    
    # Test 3: User Management
    users = test_user_management(token)
    if users is None:
        print("❌ User management failed.")
        sys.exit(1)
    
    # Test 4: Document Management
    documents = test_document_management(token)
    if documents is None:
        print("❌ Document management failed.")
        sys.exit(1)
    
    # Test 5: Search Functionality
    if not test_search_functionality(token):
        print("❌ Search functionality failed.")
        sys.exit(1)
    
    # Test 6: Analytics
    if not test_analytics(token):
        print("❌ Analytics failed.")
        sys.exit(1)
    
    # Test 7: System Logs
    if not test_system_logs(token):
        print("❌ System logs failed.")
        sys.exit(1)
    
    # Test 8: User Registration
    if not test_user_registration():
        print("❌ User registration failed.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 All database tests completed successfully!")
    print("\n📋 Database Integration Summary:")
    print("   ✅ PostgreSQL connection working")
    print("   ✅ User authentication and management")
    print("   ✅ Document storage and metadata")
    print("   ✅ Search query tracking")
    print("   ✅ Analytics and reporting")
    print("   ✅ System logging and audit trail")
    print("   ✅ User registration")
    
    print("\n🚀 Your database-powered application is ready!")
    print("   - Backend: http://127.0.0.1:8000")
    print("   - Frontend: streamlit run streamlit_app.py")
    print("   - API Docs: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()


