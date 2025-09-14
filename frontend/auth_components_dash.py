import requests
from typing import Optional, Dict, Any, List

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

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
    
    def query_documents(self, token: str, query: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """Query documents using the AI"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{self.api_base_url}/query",
                json={
                    "query": query,
                    "top_k": top_k
                },
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def get_documents(self, token: str) -> Optional[List[Dict[str, Any]]]:
        """Get list of uploaded documents"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.api_base_url}/documents",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def upload_document(self, token: str, file_content: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Upload a document"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            files = {"file": (filename, file_content)}
            response = requests.post(
                f"{self.api_base_url}/upload",
                files=files,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def delete_document(self, token: str, document_id: int) -> bool:
        """Delete a document"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.delete(
                f"{self.api_base_url}/documents/{document_id}",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

# Global session manager for Dash
class DashSessionManager:
    def __init__(self):
        self.sessions = {}
    
    def set_session(self, session_id: str, key: str, value: Any):
        """Set session value"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][key] = value
    
    def get_session(self, session_id: str, key: str, default=None):
        """Get session value"""
        return self.sessions.get(session_id, {}).get(key, default)
    
    def clear_session(self, session_id: str):
        """Clear session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def is_authenticated(self, session_id: str) -> bool:
        """Check if user is authenticated"""
        return self.get_session(session_id, "authenticated", False)
    
    def get_current_user(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current user"""
        return self.get_session(session_id, "user")
    
    def get_token(self, session_id: str) -> Optional[str]:
        """Get auth token"""
        return self.get_session(session_id, "token")
    
    def is_admin(self, session_id: str) -> bool:
        """Check if current user is admin"""
        user = self.get_current_user(session_id)
        return user and user.get("role") == "admin"

# Global session manager instance
dash_session_manager = DashSessionManager()

# Helper functions for compatibility
def is_authenticated(session_id: str = None) -> bool:
    """Check if user is authenticated"""
    if session_id is None:
        session_id = "default_session"  # In real app, get from request context
    return dash_session_manager.is_authenticated(session_id)

def get_current_user(session_id: str = None) -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if session_id is None:
        session_id = "default_session"
    return dash_session_manager.get_current_user(session_id)

def is_admin(session_id: str = None) -> bool:
    """Check if current user is admin"""
    if session_id is None:
        session_id = "default_session"
    return dash_session_manager.is_admin(session_id)

def set_auth_session(session_id: str, token: str, user_data: Dict[str, Any]):
    """Set authentication session"""
    dash_session_manager.set_session(session_id, "token", token)
    dash_session_manager.set_session(session_id, "user", user_data)
    dash_session_manager.set_session(session_id, "authenticated", True)

def clear_auth_session(session_id: str):
    """Clear authentication session"""
    dash_session_manager.clear_session(session_id)


