import streamlit as st
import sys
from pathlib import Path

# Add the frontend directory to the path to import auth components
sys.path.append(str(Path(__file__).parent))

# Import and run the authenticated version
from streamlit_app_auth import main

# Page configuration
st.set_page_config(
    page_title="SKF Orbitbot - AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    main()