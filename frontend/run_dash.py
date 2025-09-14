#!/usr/bin/env python3
"""
Run the Dash application
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dash_app import app

if __name__ == "__main__":
    print("🚀 Starting SKF Orbitbot Dash Application...")
    print("📱 Dashboard will be available at: http://localhost:8050")
    print("🔧 Backend API should be running at: http://localhost:8000")
    print("=" * 50)
    
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8050,
        dev_tools_hot_reload=True
    )
