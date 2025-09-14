#!/usr/bin/env python3
"""
Status check script for SKF Orbitbot application
"""

import requests
import sys
from datetime import datetime

def check_service(url, name, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Running (Status: {response.status_code})")
            return True
        else:
            print(f"⚠️  {name}: Running but returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {name}: Timeout - service might be slow")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    print("🔍 SKF Orbitbot Application Status Check")
    print("=" * 50)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check services
    services = [
        ("http://localhost:8000/docs", "Backend API (FastAPI)"),
        ("http://localhost:8050", "Frontend (Dash)"),
    ]
    
    results = []
    for url, name in services:
        results.append(check_service(url, name))
    
    print()
    print("📊 Summary:")
    print("-" * 30)
    
    if all(results):
        print("🎉 All services are running successfully!")
        print()
        print("🌐 Access URLs:")
        print("   • Frontend (Dash): http://localhost:8050")
        print("   • Backend API: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print()
        print("🔐 Default Admin Credentials:")
        print("   • Username: admin")
        print("   • Password: admin123")
        sys.exit(0)
    else:
        print("⚠️  Some services are not running properly.")
        print("   Please check the individual service logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()


