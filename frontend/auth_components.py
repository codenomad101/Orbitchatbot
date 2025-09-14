import streamlit as st
import requests
import json
from typing import Optional, Dict, Any, List

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Enhanced CSS for authentication components
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Auth page styling
.auth-container {
    max-width: 500px;
    margin: 2rem auto;
    padding: 2rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 254, 0.1);
    border: 1px solid rgba(0, 0, 254, 0.1);
}
 */
.auth-header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid rgba(0, 0, 254, 0.1);
}

.auth-title {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #0000fe;
    margin: 0 0 0.5rem 0;
    text-shadow: 2px 2px 4px rgba(0, 0, 254, 0.1);
}

.auth-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    color: #6c757d;
    margin: 0;
    font-weight: 400;
}

/* Form styling 
.auth-form {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 254, 0.08);
    border: 1px solid rgba(0, 0, 254, 0.1);
    margin: 1rem 0;
}*/

.form-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #0000fe;
    margin-bottom: 1.5rem;
    text-align: center;
}

/* Input field styling */
.stTextInput {
    margin-bottom: 1.5rem !important;
    width: 100% !important;
            line-height: 1.5 !important;
}

.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #e8eaed !important;
    padding: 1rem 1.5rem !important;
    font-size: 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    background: #f8f9fa !important;
    transition: all 0.3s ease !important;
    height: 4rem !important;
    line-height: 2.5 !important;
}

.stTextInput > div > div > input:focus {
    border-color: #0000fe !important;
    box-shadow: 0 0 0 3px rgba(0, 0, 254, 0.1) !important;
    background: white !important;
            
}

.stTextInput > div > div > input::placeholder {
    color: #adb5bd !important;
    font-weight: 400 !important;
}

/* Button styling */
.stButton {
    margin-top: 1rem !important;
}

.stButton > button {
    border-radius: 12px !important;
    border: none !important;
    padding: 1rem 2rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    transition: all 0.3s ease !important;
    background: linear-gradient(135deg, #0000fe 0%, #0066ff 100%) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(0, 0, 254, 0.2) !important;
    height: 4rem !important;
    min-height: 4rem !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 254, 0.3) !important;
    background: linear-gradient(135deg, #0000cc 0%, #0052cc 100%) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(0, 0, 254, 0.1) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 0, 254, 0.2) !important;
    padding: 0.8rem 1.5rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    color: #0000fe !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0000fe 0%, #0066ff 100%) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(0, 0, 254, 0.2) !important;
}

/* Info box styling */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid rgba(0, 0, 254, 0.2) !important;
    background: rgba(0, 0, 254, 0.05) !important;
}

.stSuccess {
    background: rgba(40, 167, 69, 0.1) !important;
    border: 1px solid rgba(40, 167, 69, 0.2) !important;
    color: #155724 !important;
}

.stError {
    background: rgba(220, 53, 69, 0.1) !important;
    border: 1px solid rgba(220, 53, 69, 0.2) !important;
    color: #721c24 !important;
}

/* Divider styling */
.auth-divider {
    margin: 2rem 0;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 0, 254, 0.3), transparent);
}

/* Admin info styling */
.admin-info {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border: 1px solid rgba(0, 0, 254, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.admin-info h4 {
    color: #0000fe;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}

.admin-info code {
    background: rgba(0, 0, 254, 0.1);
    color: #0000fe;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-weight: 600;
}

/* Responsive design */
@media (max-width: 768px) {
    .auth-container {
        margin: 1rem;
        padding: 1.5rem;
    }
    
    .auth-title {
        font-size: 2rem;
    }
}

/* Animation for form appearance */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.auth-form {
    animation: fadeInUp 0.6s ease-out;
}
</style>
""", unsafe_allow_html=True)

class AuthManager:
    def __init__(self):
        self.api_base_url = API_BASE_URL
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Login user and return user data with token"""
        try:
            response = requests.post(
                f"{self.api_base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def register(self, username: str, email: str, password: str, role: str = "user") -> Optional[Dict[str, Any]]:
        """Register a new user"""
        try:
            response = requests.post(
                f"{self.api_base_url}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": role
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def create_user_as_admin(self, token: str, username: str, email: str, password: str, role: str = "user") -> bool:
        """Create a new user as admin"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{self.api_base_url}/auth/users/create",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": role
                },
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user information using token"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.api_base_url}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_search_history(self, token: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get user's search history"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.api_base_url}/search/history?limit={limit}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_analytics(self, token: str) -> Optional[Dict[str, Any]]:
        """Get system analytics (Admin only)"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.api_base_url}/analytics/stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def logout(self):
        """Logout user by clearing session state"""
        for key in list(st.session_state.keys()):
            if key.startswith('auth_'):
                del st.session_state[key]
        st.rerun()

def init_session_state():
    """Initialize authentication session state"""
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_is_authenticated" not in st.session_state:
        st.session_state.auth_is_authenticated = False

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    # Session state should already be initialized by main()
    return st.session_state.auth_is_authenticated and st.session_state.auth_token is not None

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    # Session state should already be initialized by main()
    if is_authenticated():
        return st.session_state.auth_user
    return None

def is_admin() -> bool:
    """Check if current user is admin"""
    user = get_current_user()
    return user and user.get("role") == "admin"

def set_auth_session(token: str, user_data: Dict[str, Any]):
    """Set authentication session"""
    st.session_state.auth_token = token
    st.session_state.auth_user = user_data
    st.session_state.auth_is_authenticated = True

def clear_auth_session():
    """Clear authentication session"""
    st.session_state.auth_token = None
    st.session_state.auth_user = None
    st.session_state.auth_is_authenticated = False

def render_login_form():
    """Render login form"""
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">🔐 Login to Your Account</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
        
        if submit_button:
            if username and password:
                auth_manager = AuthManager()
                login_result = auth_manager.login(username, password)
                
                if login_result:
                    set_auth_session(login_result["access_token"], login_result["user"])
                    st.success("✅ Login successful! Welcome back!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
            else:
                st.error("❌ Please fill in all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_register_form():
    """Render registration form"""
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📝 Create New Account</div>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Choose a secure password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Passwords do not match. Please try again.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                else:
                    auth_manager = AuthManager()
                    register_result = auth_manager.register(username, email, password)
                    
                    if register_result:
                        st.success("✅ Registration successful! Please login with your new account.")
                        st.session_state.show_login = True
                        st.rerun()
                    else:
                        st.error("❌ Registration failed. Username might already exist.")
            else:
                st.error("❌ Please fill in all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_auth_page():
    """Render authentication page with login/register tabs"""
    # Main container with centered layout
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header section
    st.markdown("""
    <div class="auth-header">
        <div class="auth-title">🤖 SKF Orbitbot</div>
        <div class="auth-subtitle">Your Intelligent Document Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_register_form()
    
    # Add info about default admin account
    st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
    
    # st.markdown("""
    # <div class="admin-info">
    #     <h4>🔑 Default Admin Account</h4>
    #     <p><strong>Username:</strong> <code>admin</code></p>
    #     <p><strong>Password:</strong> <code>admin123</code></p>
    #     <p><em>Please change the default password after first login for security.</em></p>
    # </div>
    # """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_logout_button():
    """Render logout button in sidebar"""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        clear_auth_session()
        st.sidebar.success("👋 Logged out successfully!")
        st.rerun()

def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            render_auth_page()
            return
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin access for a function"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            render_auth_page()
            return
        if not is_admin():
            st.error("🔒 Admin access required")
            return
        return func(*args, **kwargs)
    return wrapper
