import streamlit as st
import requests
import json
from pathlib import Path
import time
import pandas as pd
from datetime import datetime

# Import authentication components
from auth_components import (
    is_authenticated, get_current_user, is_admin, 
    render_auth_page, render_logout_button,
    require_auth, require_admin, AuthManager
)

# Page configuration
st.set_page_config(
    page_title="SKF Orbitbot - AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Enhanced CSS with professional design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styling */
* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: black;
    min-height: 100vh;
}

/* Main chat interface styling */
.main-container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    margin-top: 2rem;
    margin-bottom: 2rem;
    overflow: hidden;
}

/* Header styling */
.app-header {
    background: black;
    color: 0000fe;
    padding: 2rem;
    text-align: center;
    margin: -2rem -2rem 2rem -2rem;
}

.app-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.app-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    font-weight: 300;
}

/* User info styling */
.user-info {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-name {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
}

.user-role {
    font-size: 0.9rem;
    opacity: 0.8;
    padding: 0.25rem 0.75rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    display: inline-block;
}

/* Chat message styling */
.user-message {
    background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%);
    color: white;
    padding: 1.2rem 1.8rem;
    border-radius: 20px 20px 5px 20px;
    margin: 1rem 0;
    position: relative;
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.3);
    animation: slideInRight 0.3s ease-out;
}

.assistant-message {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
    color: #333;
    padding: 1.2rem 1.8rem;
    border-radius: 20px 20px 20px 5px;
    margin: 1rem 0;
    position: relative;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
    animation: slideInLeft 0.3s ease-out;
    border: 1px solid #BBDEFB;
}

@keyframes slideInRight {
    from { transform: translateX(50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInLeft {
    from { transform: translateX(-50px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Avatar styling */
.user-avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #1976D2, #0D47A1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    position: absolute;
    right: -50px;
    top: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    font-size: 16px;
}

.assistant-avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #2196F3, #1976D2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    position: absolute;
    left: -50px;
    top: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    font-size: 18px;
}

/* Sidebar styling */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.css-1d391kg .css-1v0mbdj, [data-testid="stSidebar"] > div {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
}

/* Sidebar text styling - all white */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown div,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stText,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] label {
    color: white !important;
}

/* Sidebar cards */
.sidebar-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
    padding: 1.5rem;
    margin: -1rem -1rem 1rem -1rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(13, 71, 161, 0.3);
}

.sidebar-title {
    color: white !important;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
}

.sidebar-subtitle {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 0.9rem;
    margin: 0.5rem 0 0 0;
}

/* Status styling */
.status-healthy {
    background: blue;
    border: none;
    color: white !important;
    padding: 0.8rem;
    border-radius: 12px;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    font-weight: 500;
}

.status-unhealthy {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    border: none;
    color: white !important;
    padding: 0.8rem;
    border-radius: 12px;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
    font-weight: 500;
}

/* Sidebar buttons styling */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.3) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(25, 118, 210, 0.4) !important;
}

/* Admin badge */
.admin-badge {
    background: linear-gradient(135deg, #FF6B35, #F7931E);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
}

.user-badge {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

/* File uploader styling */
[data-testid="stSidebar"] .stFileUploader > div {
    border: 2px dashed rgba(255, 255, 255, 0.5) !important;
    border-radius: 15px;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}

[data-testid="stSidebar"] .stFileUploader > div:hover {
    border-color: rgba(255, 255, 255, 0.8) !important;
    background: rgba(255, 255, 255, 0.15);
}

[data-testid="stSidebar"] .stFileUploader label {
    color: white !important;
}

/* Source styling */
.source-container {
    background: #E3F2FD;
    border-left: 4px solid #1976D2;
    padding: 1.2rem;
    margin: 1rem 0;
    border-radius: 0 12px 12px 0;
    box-shadow: 0 2px 10px rgba(25, 118, 210, 0.1);
    transition: transform 0.2s ease;
    color: #333;
}

.source-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(25, 118, 210, 0.2);
}

.source-header {
    font-weight: 600;
    color: #1976D2;
    margin-bottom: 0.8rem;
    font-size: 0.95rem;
}

/* Welcome message */
.welcome-container {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 20px;
    color: #333;
    margin: 2rem 0;
    box-shadow: 0 15px 35px rgba(25, 118, 210, 0.1);
}

.welcome-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1976D2;
}

.welcome-subtitle {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: #666;
}

.welcome-description {
    font-size: 1rem;
    color: #666;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Input styling */
.stTextInput > div > div > input {
    border-radius: 25px;
    border: 2px solid #1976D2;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    background: white;
    color: #333;
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.1);
    transition: all 0.3s ease;
    height: 60px;
}

.stTextInput > div > div > input:focus {
    border-color: #0D47A1;
    box-shadow: 0 4px 20px rgba(13, 71, 161, 0.2);
}

/* Button styling */
.stButton > button {
    border-radius: 25px;
    border: none;
    padding: 0.8rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    color: white;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%);
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(25, 118, 210, 0.4);
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
}

/* Hide default streamlit elements */
.stDeployButton {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Loading animation */
.stSpinner {
    text-align: center;
}

.stSpinner > div {
    color: #1976D2;
}

/* Access denied styling */
.access-denied {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border-radius: 20px;
    color: #c62828;
    margin: 2rem 0;
    border: 2px solid #ef5350;
}

.access-denied-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.access-denied-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.access-denied-message {
    font-size: 1rem;
    opacity: 0.8;
}

</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def upload_file(file, token):
    """Upload a file to the API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Upload failed with status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def query_documents(question, top_k=5, token=None):
    """Query the document collection"""
    try:
        data = {"question": question, "top_k": top_k}
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.post(
            f"{API_BASE_URL}/query", 
            json=data,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Query failed with status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def get_documents(token):
    """Get list of stored documents"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/documents", headers=headers, timeout=10)
        if response.status_code == 200:
            documents = response.json()
            # Convert to old format for compatibility
            total_documents = len(documents)
            total_chunks = sum(doc.get('total_chunks', 0) for doc in documents)
            
            return True, {
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "documents": [
                    {
                        "filename": doc["original_filename"],
                        "chunks": doc.get("total_chunks", 0),
                        "id": doc["id"],
                        "status": doc.get("processing_status", "unknown")
                    }
                    for doc in documents
                ]
            }
        else:
            return False, {"error": f"Failed to fetch documents: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def delete_document(document_id, token):
    """Delete a document"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{API_BASE_URL}/documents/{document_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Failed to delete document: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def render_message(message, is_user=True):
    """Render a chat message with proper styling"""
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <div class="user-avatar">👤</div>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <div class="assistant-avatar">🤖</div>
            {message}
        </div>
        """, unsafe_allow_html=True)

def render_sources(sources):
    """Render source information"""
    if sources:
        st.markdown("### 📚 **Source References**")
        for i, source in enumerate(sources, 1):
            with st.expander(f"🔍 **Source {i}:** {source.get('file_name', 'Unknown')} | Relevance: {source.get('similarity_score', 0):.1%}", expanded=False):
                st.markdown(f"""
                <div class="source-container">
                    <div class="source-header">📄 Document Section #{source.get('chunk_id', 'N/A')}</div>
                    <div style="line-height: 1.6;">
                        {source['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_user_management():
    """Render user management interface for admins"""
    st.markdown("### 👥 User Management")
    
    auth_manager = AuthManager()
    token = st.session_state.auth_token
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/auth/users", headers=headers, timeout=10)
        
        if response.status_code == 200:
            users = response.json()
            
            if users:
                st.markdown(f"**Total Users:** {len(users)}")
                
                # User management options
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown("**User Actions:**")
                with col2:
                    if st.button("🔄 Refresh", use_container_width=True):
                        st.rerun()
                with col3:
                    if st.button("📊 Analytics", use_container_width=True):
                        st.session_state.show_user_analytics = True
                
                # Add new user section
                if st.button("➕ Add New User", use_container_width=True):
                    st.session_state.show_add_user = True
                
                if st.session_state.get('show_add_user', False):
                    render_add_user_form()
                    if st.button("❌ Cancel"):
                        st.session_state.show_add_user = False
                        st.rerun()
                    return
                
                if st.session_state.get('show_user_analytics', False):
                    render_user_analytics(users)
                    if st.button("❌ Close Analytics"):
                        st.session_state.show_user_analytics = False
                        st.rerun()
                    return
                
                for user in users:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**👤 {user['username']}**")
                            st.caption(f"📧 {user['email']}")
                            if user.get('last_login'):
                                st.caption(f"🕒 Last login: {user['last_login'][:10]}")
                            st.caption(f"📅 Created: {user['created_at'][:10]}")
                        
                        with col2:
                            # Role selection
                            current_role = user['role']
                            if user['id'] != get_current_user()['id']:  # Don't allow changing own role
                                new_role = st.selectbox(
                                    "Role",
                                    ["user", "admin"],
                                    index=0 if current_role == "user" else 1,
                                    key=f"role_{user['id']}",
                                    label_visibility="collapsed"
                                )
                                
                                if new_role != current_role:
                                    if st.button("💾", key=f"update_role_{user['id']}", help="Update role"):
                                        update_response = requests.put(
                                            f"{API_BASE_URL}/auth/users/{user['id']}/role",
                                            json={"role": new_role},
                                            headers=headers,
                                            timeout=10
                                        )
                                        if update_response.status_code == 200:
                                            st.success("✅ Role updated!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to update role")
                            else:
                                role_badge = "admin-badge" if current_role == 'admin' else "user-badge"
                                st.markdown(f'<span class="{role_badge}">{current_role.upper()}</span>', unsafe_allow_html=True)
                                st.caption("(Your account)")
                            
                            # Status
                            status_text = "ACTIVE" if user['is_active'] else "INACTIVE"
                            status_color = "🟢" if user['is_active'] else "🔴"
                            st.caption(f"{status_color} {status_text}")
                        
                        with col3:
                            if user['id'] != get_current_user()['id']:  # Don't allow deactivating self
                                if user['is_active']:
                                    if st.button("🗑️", key=f"deactivate_{user['id']}", help="Deactivate user", use_container_width=True):
                                        deactivate_response = requests.put(
                                            f"{API_BASE_URL}/auth/users/{user['id']}/deactivate",
                                            headers=headers,
                                            timeout=10
                                        )
                                        if deactivate_response.status_code == 200:
                                            st.success("✅ User deactivated!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to deactivate user")
                                else:
                                    st.caption("Inactive")
                        
                        with col4:
                            # View user details
                            if st.button("👁️", key=f"view_{user['id']}", help="View details", use_container_width=True):
                                st.session_state.selected_user = user
                                st.rerun()
                        
                        st.markdown("---")
            else:
                st.info("No users found")
        else:
            st.error("Failed to fetch users")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching users: {str(e)}")

def render_user_analytics(users):
    """Render user analytics dashboard"""
    st.markdown("### 📊 User Analytics")
    
    # Calculate statistics
    total_users = len(users)
    active_users = len([u for u in users if u['is_active']])
    admin_users = len([u for u in users if u['role'] == 'admin'])
    user_users = len([u for u in users if u['role'] == 'user'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Active Users", active_users, f"{active_users/total_users*100:.1f}%" if total_users > 0 else "0%")
    with col3:
        st.metric("Admins", admin_users, f"{admin_users/total_users*100:.1f}%" if total_users > 0 else "0%")
    with col4:
        st.metric("Regular Users", user_users, f"{user_users/total_users*100:.1f}%" if total_users > 0 else "0%")
    
    # Role distribution chart
    st.markdown("#### 📈 Role Distribution")
    role_data = {
        'Admin': admin_users,
        'User': user_users
    }
    st.bar_chart(role_data)
    
    # Recent activity
    st.markdown("#### 🕒 Recent Activity")
    recent_users = sorted([u for u in users if u.get('last_login')], 
                         key=lambda x: x['last_login'], reverse=True)[:5]
    
    for user in recent_users:
        st.caption(f"👤 {user['username']} - Last login: {user['last_login'][:16]}")

def render_add_user_form():
    """Render form to add new users"""
    st.markdown("### ➕ Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username", placeholder="Enter username")
            new_email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Enter password")
            new_role = st.selectbox("Role", ["user", "admin"], index=0)
        
        submit_button = st.form_submit_button("Create User", type="primary", use_container_width=True)
        
        if submit_button:
            if new_username and new_email and new_password:
                if len(new_password) >= 6:
                    auth_manager = AuthManager()
                    success = auth_manager.create_user_as_admin(
                        st.session_state.auth_token,
                        new_username, 
                        new_email, 
                        new_password, 
                        new_role
                    )
                    
                    if success:
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.session_state.show_add_user = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to create user. Username might already exist.")
                else:
                    st.error("❌ Password must be at least 6 characters long.")
            else:
                st.error("❌ Please fill in all fields.")

def render_user_details():
    """Render detailed user information"""
    if 'selected_user' in st.session_state and st.session_state.selected_user is not None:
        user = st.session_state.selected_user
        
        st.markdown("### 👤 User Details")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Role:** {user['role'].upper()}")
            st.markdown(f"**Status:** {'🟢 ACTIVE' if user['is_active'] else '🔴 INACTIVE'}")
            st.markdown(f"**Created:** {user['created_at']}")
            if user.get('last_login'):
                st.markdown(f"**Last Login:** {user['last_login']}")
        
        with col2:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.selected_user = None
                st.rerun()
        
        st.markdown("---")
        
        # User activity summary (placeholder)
        st.markdown("#### 📊 Activity Summary")
        st.info("User activity tracking will be implemented with search history and document access logs.")
        
        return True
    return False

@require_auth
def render_main_interface():
    """Render the main application interface"""
    user = get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">🤖 SKF Orbitbot</div>
            <div class="sidebar-subtitle">Your Intelligent Document Assistant</div>
        </div>
        """, unsafe_allow_html=True)
        
        # User info
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### 👤 User Info")
        role_badge = "admin-badge" if user['role'] == 'admin' else "user-badge"
        st.markdown(f"""
        <div class="user-info">
            <div class="user-name">👤 {user['username']}</div>
            <div class="user-role">
                <span class="{role_badge}">{user['role'].upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_logout_button()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System Status Section
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ System Status")
        health_ok, health_data = check_api_health()
        
        if health_ok:
            st.markdown('<div class="status-healthy">🟢 Connected & Ready</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-unhealthy">🔴 Connection Failed</div>', unsafe_allow_html=True)
            st.error("🚫 Backend not accessible at http://127.0.0.1:8000")
            st.info("💡 Please start the backend server to continue")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Admin-only sections
        if is_admin():
            # Document Upload Section
            st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
            st.markdown("### 📤 Upload Documents")
            
            uploaded_file = st.file_uploader(
                "Drop your files here or browse",
                type=['pdf', 'docx', 'txt'],
                help="📋 Supported formats: PDF, DOCX, TXT files"
            )
            
            if uploaded_file is not None:
                st.markdown(f"**📄 {uploaded_file.name}**")
                st.caption(f"💾 Size: {uploaded_file.size:,} bytes")
                
                if st.button("🚀 Upload", type="primary", use_container_width=True, key="upload_btn"):
                    with st.spinner("🔄 Processing document..."):
                        success, result = upload_file(uploaded_file, st.session_state.auth_token)
                        if success:
                            st.success("✅ Successfully uploaded!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Upload failed")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Document Management Section
            st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
            st.markdown("### 📚 Knowledge Base")
            
            docs_ok, docs_data = get_documents(st.session_state.auth_token)
            if docs_ok:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📄 Documents", docs_data.get("total_documents", 0))
                with col2:
                    st.metric("🧩 Text Chunks", docs_data.get("total_chunks", 0))
                
                if docs_data.get("documents"):
                    with st.expander("📋 **Document Library** (Click to expand)", expanded=True):
                        for doc in docs_data["documents"]:
                            with st.container():
                                col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**📄 {doc['filename']}**")
                                st.caption(f"🧩 {doc['chunks']} chunks | Status: {doc.get('status', 'unknown')}")
                            with col2:
                                if st.button("🗑️", key=f"del_{doc['id']}", help="Delete document", use_container_width=True):
                                    with st.spinner("Deleting..."):
                                        success, result = delete_document(doc['id'], st.session_state.auth_token)
                                        if success:
                                            st.success("🗑️ Deleted!")
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error("❌ Delete failed")
                                st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # User Management Section
            st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
            
            # Check if user details should be shown
            if render_user_details():
                pass  # User details already rendered
            else:
                render_user_management()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # User profile and search history (visible to all users)
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### 👤 My Profile")
        
        user = get_current_user()
        
        # Profile information
        st.markdown(f"**Username:** {user['username']}")
        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Role:** {user['role'].upper()}")
        st.markdown(f"**Status:** {'🟢 ACTIVE' if user['is_active'] else '🔴 INACTIVE'}")
        if user.get('last_login'):
            st.markdown(f"**Last Login:** {user['last_login'][:16]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Search History")
        
        try:
            auth_manager = AuthManager()
            history = auth_manager.get_search_history(st.session_state.auth_token, limit=10)
            
            if history:
                for query in history[:5]:  # Show last 5 queries
                    st.caption(f"🔍 {query['query'][:50]}{'...' if len(query['query']) > 50 else ''}")
                    st.caption(f"📅 {query['created_at'][:16]}")
                    st.markdown("---")
            else:
                st.info("No search history available")
        except Exception as e:
            st.error("Failed to load search history")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Settings Section
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Assistant Settings")
        top_k = st.slider("🔍 Sources per response", 1, 10, 5, help="Number of document sources to reference")
        show_sources = st.checkbox("📚 Show source references", value=True, help="Display document sources used in responses")
        
        # Clear chat button
        if st.button("🧹 Clear Conversation", type="secondary", help="Start a fresh conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_input_key += 1
            st.success("🗑️ Conversation cleared!")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="app-header">
        <div class="app-title">🤖 SKF Orbitbot</div>
        <div class="app-subtitle">Welcome back, {user['username']}! 👋</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message when no conversation exists
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">🤖 SKF Orbitbot</div>
            <div class="welcome-subtitle">Your Advanced AI Document Assistant</div>
            <div class="welcome-description">
                Hello! I'm Orbitbot, your intelligent document companion. I can help you explore, analyze, 
                and extract insights from your uploaded documents. 
                {'Upload your files using the sidebar and ' if is_admin() else ''}Start asking questions!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            render_message(message["content"], is_user=True)
        else:
            render_message(message["content"], is_user=False)
            # Show sources if available
            if show_sources and "sources" in message:
                render_sources(message["sources"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input(
        "Message",
        placeholder="💬 Ask Orbitbot anything about your documents...",
        key=f"chat_input_{st.session_state.chat_input_key}",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("🚀 Send", type="primary", disabled=not user_input.strip(), use_container_width=True)
    
    # Handle user input
    if send_button and user_input.strip():
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        with st.spinner("🧠 Orbitbot is thinking..."):
            success, result = query_documents(user_input.strip(), top_k, st.session_state.auth_token)
            
            if success:
                # Add assistant response to chat history
                assistant_message = {
                    "role": "assistant", 
                    "content": result["answer"]
                }
                if result.get("sources"):
                    assistant_message["sources"] = result["sources"]
                
                st.session_state.messages.append(assistant_message)
            else:
                # Add error message
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"🚫 **Oops!** I encountered an issue: {result.get('error', 'Unknown error')}\n\nPlease try again or check if your documents are properly uploaded."
                })
        
        # Increment input key to reset the input field
        st.session_state.chat_input_key += 1
        st.rerun()

def init_all_session_state():
    """Initialize all session state variables"""
    # Initialize auth session state
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_is_authenticated" not in st.session_state:
        st.session_state.auth_is_authenticated = False
    
    # Initialize app session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    if "show_user_analytics" not in st.session_state:
        st.session_state.show_user_analytics = False
    if "show_add_user" not in st.session_state:
        st.session_state.show_add_user = False
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None
    if "show_login" not in st.session_state:
        st.session_state.show_login = True  # Default to showing login form

def main():
    """Main application function"""
    # Initialize all session state variables first
    init_all_session_state()
    
    if not is_authenticated():
        render_auth_page()
    else:
        render_main_interface()

if __name__ == "__main__":
    main()
