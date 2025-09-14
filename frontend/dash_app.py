import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional
import base64
import io

# Import authentication components
from auth_components_dash import (
    AuthManager, dash_session_manager, is_authenticated, 
    get_current_user, is_admin, set_auth_session, clear_auth_session
)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# App configuration
app.title = "SKF Orbitbot - AI Assistant"

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

def get_session_id():
    """Get current session ID"""
    # In a real app, you'd get this from the request context
    return "default_session"

# Authentication layout
def create_auth_layout():
    """Create authentication page layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H1("🤖 SKF Orbitbot", className="text-center mb-3", 
                                   style={"color": "#0000fe", "fontWeight": "700"}),
                            html.P("Your Intelligent Document Assistant", 
                                  className="text-center text-muted mb-4")
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                html.Div([
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-user")]),
                                        dbc.Input(id="login-username", placeholder="Enter your username", 
                                                 type="text", className="mb-3")
                                    ]),
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-lock")]),
                                        dbc.Input(id="login-password", placeholder="Enter your password", 
                                                 type="password", className="mb-3")
                                    ]),
                                    dbc.Button("🚀 Login", id="login-btn", color="primary", 
                                              className="w-100 mb-3", size="lg")
                                ])
                            ], label="🔐 Login", tab_id="login"),
                            dbc.Tab([
                                html.Div([
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-user")]),
                                        dbc.Input(id="register-username", placeholder="Choose a username", 
                                                 type="text", className="mb-3")
                                    ]),
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-envelope")]),
                                        dbc.Input(id="register-email", placeholder="Enter your email", 
                                                 type="email", className="mb-3")
                                    ]),
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-lock")]),
                                        dbc.Input(id="register-password", placeholder="Choose a password", 
                                                 type="password", className="mb-3")
                                    ]),
                                    dbc.InputGroup([
                                        dbc.InputGroupText([html.I(className="fas fa-lock")]),
                                        dbc.Input(id="register-confirm-password", placeholder="Confirm password", 
                                                 type="password", className="mb-3")
                                    ]),
                                    dbc.Button("🚀 Create Account", id="register-btn", color="primary", 
                                              className="w-100 mb-3", size="lg")
                                ])
                            ], label="📝 Register", tab_id="register")
                        ]),
                        html.Hr(),
                        dbc.Alert([
                            html.H5("🔑 Default Admin Account", className="mb-2"),
                            html.P([
                                html.Strong("Username: "), 
                                dbc.Badge("admin", color="primary", className="me-2"),
                                html.Br(),
                                html.Strong("Password: "), 
                                dbc.Badge("admin123", color="primary", className="me-2")
                            ], className="mb-0")
                        ], color="info")
                    ])
                ], className="shadow-lg border-0", style={"maxWidth": "500px", "margin": "0 auto"})
            ], width=12)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True, className="bg-light")

# Main application layout
def create_main_layout():
    """Create main application layout"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H1("🤖 SKF Orbitbot", className="text-center mb-2", 
                                   style={"color": "#0000fe", "fontWeight": "700"}),
                            html.P("Welcome back! 👋", className="text-center text-muted mb-0")
                        ])
                    ])
                ], className="border-0 bg-transparent")
            ])
        ], className="mb-4"),
        
        # Main content area
        dbc.Row([
            # Sidebar
            dbc.Col([
                create_sidebar()
            ], width=3, className="pe-3"),
            
            # Main chat area
            dbc.Col([
                create_chat_area()
            ], width=9, className="ps-3")
        ])
    ], fluid=True, className="bg-light")

def create_sidebar():
    """Create sidebar with user info and controls"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("📋 Control Panel", className="mb-0", style={"color": "#0000fe"})
        ]),
        dbc.CardBody([
            # User info
            dbc.Alert([
                html.H6("👤 User Info", className="mb-2"),
                html.Div(id="user-info-display")
            ], color="light", className="mb-3"),
            
            # Admin features (if admin)
            html.Div(id="admin-features"),
            
            # User features
            html.Div([
                dbc.Button("🔍 Search History", id="search-history-btn", 
                          color="outline-primary", className="w-100 mb-2"),
                dbc.Button("⚙️ Settings", id="settings-btn", 
                          color="outline-secondary", className="w-100 mb-2"),
                dbc.Button("🚪 Logout", id="logout-btn", 
                          color="danger", className="w-100")
            ], id="user-features"),
            
            # System status
            html.Hr(),
            html.H6("⚡ System Status", className="mb-2"),
            html.Div(id="system-status")
        ])
    ], className="h-100")

def create_chat_area():
    """Create main chat area"""
    return dbc.Card([
        dbc.CardBody([
            # Chat messages area
            html.Div([
                html.Div(id="chat-messages", className="mb-3", 
                        style={"height": "500px", "overflowY": "auto", "border": "1px solid #dee2e6", 
                               "borderRadius": "10px", "padding": "20px", "backgroundColor": "#f8f9fa"})
            ]),
            
            # Chat input area
            html.Div([
                dbc.InputGroup([
                    dbc.Input(id="chat-input", placeholder="💬 Ask Orbitbot anything about your documents...",
                             type="text", className="border-0"),
                    dbc.Button("🚀 Send", id="send-btn", color="primary", size="lg")
                ], size="lg")
            ])
        ])
    ], className="h-100")

# Callbacks for authentication
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
    prevent_initial_call=False
)
def display_page(pathname):
    """Display appropriate page based on authentication status"""
    session_id = get_session_id()
    is_auth = dash_session_manager.is_authenticated(session_id)
    print(f"DEBUG: Session ID: {session_id}")
    print(f"DEBUG: Is authenticated: {is_auth}")
    print(f"DEBUG: Session data: {dash_session_manager.sessions}")
    
    if is_auth:
        return create_main_layout()
    else:
        return create_auth_layout()

@app.callback(
    [Output("login-alert", "children", allow_duplicate=True),
     Output("login-alert", "is_open", allow_duplicate=True),
     Output("login-username", "value", allow_duplicate=True),
     Output("login-password", "value", allow_duplicate=True),
     Output("page-content", "children", allow_duplicate=True)],
    [Input("login-btn", "n_clicks")],
    [State("login-username", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Handle login form submission"""
    if not n_clicks:
        raise PreventUpdate
    
    if not username or not password:
        return "❌ Please fill in all fields", True, username, password, no_update
    
    auth_manager = AuthManager()
    login_result = auth_manager.login(username, password)
    
    if login_result:
        session_id = get_session_id()
        set_auth_session(session_id, login_result["access_token"], login_result["user"])
        # Return to main layout after successful login
        return "✅ Login successful!", True, "", "", create_main_layout()
    else:
        return "❌ Invalid username or password", True, username, password, no_update

@app.callback(
    [Output("register-alert", "children", allow_duplicate=True),
     Output("register-alert", "is_open", allow_duplicate=True),
     Output("register-username", "value", allow_duplicate=True),
     Output("register-email", "value", allow_duplicate=True),
     Output("register-password", "value", allow_duplicate=True),
     Output("register-confirm-password", "value", allow_duplicate=True)],
    [Input("register-btn", "n_clicks")],
    [State("register-username", "value"),
     State("register-email", "value"),
     State("register-password", "value"),
     State("register-confirm-password", "value")],
    prevent_initial_call=True
)
def handle_register(n_clicks, username, email, password, confirm_password):
    """Handle registration form submission"""
    if not n_clicks:
        raise PreventUpdate
    
    if not all([username, email, password, confirm_password]):
        return "❌ Please fill in all fields", True, username, email, password, confirm_password
    
    if password != confirm_password:
        return "❌ Passwords do not match", True, username, email, password, confirm_password
    
    if len(password) < 6:
        return "❌ Password must be at least 6 characters long", True, username, email, password, confirm_password
    
    auth_manager = AuthManager()
    register_result = auth_manager.register(username, email, password)
    
    if register_result:
        return "✅ Registration successful! Please login.", True, "", "", "", ""
    else:
        return "❌ Registration failed. Username might already exist.", True, username, email, password, confirm_password

# Callback for logout
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    [Input("logout-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if n_clicks:
        session_id = get_session_id()
        clear_auth_session(session_id)
        return create_auth_layout()
    raise PreventUpdate

# Callback for user info display
@app.callback(
    Output("user-info-display", "children"),
    [Input("page-content", "children")],
    prevent_initial_call=True
)
def update_user_info(children):
    """Update user info display"""
    session_id = get_session_id()
    user = dash_session_manager.get_current_user(session_id)
    
    if user:
        role_badge = dbc.Badge("ADMIN", color="danger") if user["role"] == "admin" else dbc.Badge("USER", color="primary")
        return [
            html.P([html.Strong("Username: "), user["username"]]),
            html.P([html.Strong("Email: "), user["email"]]),
            html.P([html.Strong("Role: "), role_badge]),
            html.P([html.Strong("Status: "), 
                   dbc.Badge("ACTIVE", color="success") if user.get("is_active", True) else dbc.Badge("INACTIVE", color="secondary")])
        ]
    return "No user data"

# Callback for admin features
@app.callback(
    Output("admin-features", "children"),
    [Input("page-content", "children")],
    prevent_initial_call=True
)
def update_admin_features(children):
    """Update admin features display"""
    session_id = get_session_id()
    
    if dash_session_manager.is_admin(session_id):
        return [
            html.Hr(),
            html.H6("🔧 Admin Features", className="mb-2"),
            dbc.Button("📤 Upload Documents", id="upload-btn", 
                      color="outline-primary", className="w-100 mb-2"),
            dbc.Button("📚 Manage Documents", id="manage-docs-btn", 
                      color="outline-primary", className="w-100 mb-2"),
            dbc.Button("👥 User Management", id="user-mgmt-btn", 
                      color="outline-primary", className="w-100 mb-2"),
            dbc.Button("📊 Analytics", id="analytics-btn", 
                      color="outline-primary", className="w-100 mb-2")
        ]
    return None

# Chat functionality callbacks
@app.callback(
    [Output("chat-messages", "children"),
     Output("chat-input", "value")],
    [Input("send-btn", "n_clicks"),
     Input("chat-input", "n_submit")],
    [State("chat-input", "value")],
    prevent_initial_call=True
)
def handle_chat(n_clicks, n_submit, message):
    """Handle chat message sending"""
    if not (n_clicks or n_submit) or not message:
        raise PreventUpdate
    
    session_id = get_session_id()
    token = dash_session_manager.get_token(session_id)
    
    if not token:
        raise PreventUpdate
    
    # Get existing messages
    messages = dash_session_manager.get_session(session_id, "messages", [])
    
    # Add user message
    messages.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Send to AI
    auth_manager = AuthManager()
    result = auth_manager.query_documents(token, message)
    
    if result and "response" in result:
        messages.append({
            "role": "assistant",
            "content": result["response"],
            "sources": result.get("sources", []),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    else:
        messages.append({
            "role": "assistant",
            "content": "🚫 Sorry, I encountered an error. Please try again.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    # Store messages
    dash_session_manager.set_session(session_id, "messages", messages)
    
    # Render messages
    return render_chat_messages(messages), ""

def render_chat_messages(messages):
    """Render chat messages"""
    if not messages:
        return html.Div([
            html.Div([
                html.H3("🤖 SKF Orbitbot", className="text-center mb-3", style={"color": "#0000fe"}),
                html.P("Your Advanced AI Document Assistant", className="text-center text-muted mb-3"),
                html.P([
                    "Hello! I'm Orbitbot, your intelligent document companion. ",
                    "I can help you explore, analyze, and extract insights from your uploaded documents. ",
                    "Start asking questions!"
                ], className="text-center")
            ], className="text-center p-4")
        ])
    
    rendered_messages = []
    for msg in messages:
        if msg["role"] == "user":
            rendered_messages.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Strong("👤 You"),
                            html.Small(f" • {msg['timestamp']}", className="text-muted ms-2")
                        ], className="mb-2"),
                        html.P(msg["content"], className="mb-0")
                    ])
                ], className="mb-3 bg-primary text-white", inverse=True)
            )
        else:
            sources_html = []
            if "sources" in msg and msg["sources"]:
                sources_html.append(html.Hr())
                sources_html.append(html.P("📚 Sources:", className="mb-2"))
                for source in msg["sources"][:3]:  # Show max 3 sources
                    sources_html.append(
                        html.P([
                            html.Strong(f"📄 {source.get('filename', 'Unknown')}"),
                            f" (Page {source.get('page_number', 'N/A')})"
                        ], className="mb-1 text-muted small")
                    )
            
            rendered_messages.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Strong("🤖 Orbitbot"),
                            html.Small(f" • {msg['timestamp']}", className="text-muted ms-2")
                        ], className="mb-2"),
                        html.P(msg["content"], className="mb-0"),
                        *sources_html
                    ])
                ], className="mb-3 bg-light")
            )
    
    return rendered_messages

# Callback for initial chat messages display
@app.callback(
    Output("chat-messages", "children", allow_duplicate=True),
    [Input("page-content", "children")],
    prevent_initial_call=True
)
def display_initial_chat(children):
    """Display initial chat messages"""
    session_id = get_session_id()
    messages = dash_session_manager.get_session(session_id, "messages", [])
    return render_chat_messages(messages)

# Main app layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-store"),
    html.Div(id="page-content"),
    
    # Alert components for feedback
    dbc.Alert(id="login-alert", is_open=False, dismissable=True, duration=4000),
    dbc.Alert(id="register-alert", is_open=False, dismissable=True, duration=4000),
])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
