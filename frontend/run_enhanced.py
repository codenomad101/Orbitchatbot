#!/usr/bin/env python3
"""
Run script for the Enhanced SKF Orbitbot Dash Application
"""

from dash_app_enhanced import app

if __name__ == "__main__":
    print("🚀 Starting Enhanced SKF Orbitbot Dash Application...")
    print("📱 Dashboard will be available at: http://localhost:8052")
    print("🔧 Backend API should be running at: http://localhost:8000")
    print("=" * 60)
    
    try:
        app.run(debug=True, host="0.0.0.0", port=8052)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


