import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import time
import base64
import io
from auth_components_dash import AuthManager, dash_session_manager

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "SKF Orbitbot - Enhanced Version"

def get_session_id():
    return "default_session"

# Enhanced auth layout
def create_auth_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H1("🤖 SKF Orbitbot", className="text-center", style={"color": "#0000fe"})
                    ]),
                    dbc.CardBody([
                        dbc.Tabs([
                            # Login Tab
                            dbc.Tab([
                                dbc.InputGroup([
                                    dbc.InputGroupText("👤"),
                                    dbc.Input(id="username", placeholder="Username", value="admin")
                                ], className="mb-3"),
                                
                                dbc.InputGroup([
                                    dbc.InputGroupText("🔒"),
                                    dbc.Input(id="password", placeholder="Password", type="password", value="admin123")
                                ], className="mb-3"),
                                
                                dbc.Button("Login", id="login-btn", color="primary", className="w-100 mb-3", size="lg"),
                                
                                dbc.Alert(id="login-alert", is_open=False)
                            ], label="🔑 Login"),
                            
                            # Register Tab
                            dbc.Tab([
                                dbc.InputGroup([
                                    dbc.InputGroupText("👤"),
                                    dbc.Input(id="register-username", placeholder="Username")
                                ], className="mb-3"),
                                
                                dbc.InputGroup([
                                    dbc.InputGroupText("📧"),
                                    dbc.Input(id="register-email", placeholder="Email", type="email")
                                ], className="mb-3"),
                                
                                dbc.InputGroup([
                                    dbc.InputGroupText("🔒"),
                                    dbc.Input(id="register-password", placeholder="Password", type="password")
                                ], className="mb-3"),
                                
                                dbc.InputGroup([
                                    dbc.InputGroupText("🔒"),
                                    dbc.Input(id="register-confirm-password", placeholder="Confirm Password", type="password")
                                ], className="mb-3"),
                                
                                dbc.Button("Register", id="register-btn", color="success", className="w-100 mb-3", size="lg"),
                                
                                dbc.Alert(id="register-alert", is_open=False)
                            ], label="📝 Register")
                        ])
                    ])
                ], className="shadow-lg", style={"maxWidth": "500px", "margin": "0 auto"})
            ], width=12)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True)

# Enhanced main layout with tabs
def create_main_layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("🤖 SKF Orbitbot", className="text-center mb-2", style={"color": "#0000fe"}),
                    html.P("AI Document Assistant", className="text-center text-muted mb-0")
                ])
            ])
        ], className="mb-4"),
        
        # Main content with tabs
        dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    # Chat Tab
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardBody([
                                # Chat messages
                                html.Div(id="chat-messages", style={
                                    "height": "500px", 
                                    "overflow-y": "auto", 
                                    "border": "1px solid #dee2e6", 
                                    "border-radius": "0.375rem", 
                                    "padding": "1rem", 
                                    "margin-bottom": "1rem",
                                    "background-color": "#f8f9fa"
                                }),
                                
                                # Chat input
                                dbc.InputGroup([
                                    dbc.Input(id="chat-input", placeholder="Ask me anything about your documents...", type="text"),
                                    dbc.Button("Send", id="send-btn", color="primary")
                                ])
                            ])
                        ])
                    ], label="💬 Chat", tab_id="chat-tab"),
                    
                    # Documents Tab (Admin only)
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("📄 Document Management")
                            ]),
                            dbc.CardBody([
                                # Upload Section
                                html.Div([
                                    html.H5("📤 Upload Documents", className="mb-3"),
                                    dcc.Upload(
                                        id='upload-data',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select Files')
                                        ]),
                                        style={
                                            'width': '100%',
                                            'height': '60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px'
                                        },
                                        multiple=True
                                    ),
                                    html.Div(id='upload-output')
                                ], className="mb-4"),
                                
                                # Document List
                                html.Div([
                                    html.H5("📋 Uploaded Documents", className="mb-3"),
                                    html.Div(id="document-list")
                                ])
                            ])
                        ])
                    ], label="📄 Documents", tab_id="documents-tab"),
                    
                    # Users Tab (Admin only)
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("👥 User Management")
                            ]),
                            dbc.CardBody([
                                # Create User Section
                                html.Div([
                                    html.H5("➕ Create New User", className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Input(id="new-user-username", placeholder="Username", className="mb-2")
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Input(id="new-user-email", placeholder="Email", type="email", className="mb-2")
                                        ], width=6)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Input(id="new-user-password", placeholder="Password", type="password", className="mb-2")
                                        ], width=6),
                                        dbc.Col([
                                            dbc.Select(
                                                id="new-user-role",
                                                options=[
                                                    {"label": "User", "value": "user"},
                                                    {"label": "Admin", "value": "admin"}
                                                ],
                                                value="user",
                                                className="mb-2"
                                            )
                                        ], width=6)
                                    ]),
                                    dbc.Button("Create User", id="create-user-btn", color="primary", className="mb-3"),
                                    html.Div(id="create-user-output")
                                ], className="mb-4"),
                                
                                html.Hr(),
                                
                                # User List
                                html.Div([
                                    html.H5("👥 All Users", className="mb-3"),
                                    html.Div(id="user-list")
                                ])
                            ])
                        ])
                    ], label="👥 Users", tab_id="users-tab"),
                    
                    # Analytics Tab (Admin only)
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H4("📊 Analytics Dashboard")
                            ]),
                            dbc.CardBody([
                                html.Div(id="analytics-content")
                            ])
                        ])
                    ], label="📊 Analytics", tab_id="analytics-tab")
                    
                ], id="main-tabs", active_tab="chat-tab")
            ], width=12)
        ]),
        
        # User info in sidebar
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="user-info-display"),
                        html.Hr(),
                        dbc.Button("🚪 Logout", id="logout-btn", color="danger", className="w-100")
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ], fluid=True)

# App layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
    # Hidden div for loading states
    html.Div(id="loading-states", style={"display": "none"})
])

# Main page callback
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
    prevent_initial_call=False
)
def display_page(pathname):
    session_id = get_session_id()
    is_auth = dash_session_manager.is_authenticated(session_id)
    
    if is_auth:
        return create_main_layout()
    else:
        return create_auth_layout()

# Login callback
@app.callback(
    [Output("login-alert", "children"),
     Output("login-alert", "is_open"),
     Output("login-alert", "color"),
     Output("page-content", "children", allow_duplicate=True)],
    [Input("login-btn", "n_clicks")],
    [State("username", "value"),
     State("password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if not n_clicks:
        raise PreventUpdate
    
    if not username or not password:
        return "Please fill in all fields", True, "danger", no_update
    
    auth_manager = AuthManager()
    result = auth_manager.login(username, password)
    
    if result:
        session_id = get_session_id()
        dash_session_manager.set_session(session_id, "authenticated", True)
        dash_session_manager.set_session(session_id, "user", result["user"])
        dash_session_manager.set_session(session_id, "token", result["access_token"])
        
        return "Login successful!", True, "success", create_main_layout()
    else:
        return "Invalid credentials", True, "danger", no_update

# Register callback
@app.callback(
    [Output("register-alert", "children"),
     Output("register-alert", "is_open"),
     Output("register-alert", "color"),
     Output("register-username", "value"),
     Output("register-email", "value"),
     Output("register-password", "value"),
     Output("register-confirm-password", "value")],
    [Input("register-btn", "n_clicks")],
    [State("register-username", "value"),
     State("register-email", "value"),
     State("register-password", "value"),
     State("register-confirm-password", "value")],
    prevent_initial_call=True
)
def handle_register(n_clicks, username, email, password, confirm_password):
    if not n_clicks:
        raise PreventUpdate
    
    if not all([username, email, password, confirm_password]):
        return "Please fill in all fields", True, "danger", username, email, password, confirm_password
    
    if password != confirm_password:
        return "Passwords do not match", True, "danger", username, email, password, confirm_password
    
    auth_manager = AuthManager()
    result = auth_manager.register(username, email, password)
    
    if result:
        return "Registration successful! Please login.", True, "success", "", "", "", ""
    else:
        return "Registration failed. Username might already exist.", True, "danger", username, email, password, confirm_password

# Logout callback
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    [Input("logout-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        session_id = get_session_id()
        dash_session_manager.clear_session(session_id)
        return create_auth_layout()
    raise PreventUpdate

# User info callback
@app.callback(
    Output("user-info-display", "children"),
    [Input("page-content", "children")],
    prevent_initial_call=True
)
def update_user_info(children):
    session_id = get_session_id()
    user = dash_session_manager.get_current_user(session_id)
    
    if user:
        role_badge = dbc.Badge("Admin", color="danger") if user['role'] == 'admin' else dbc.Badge("User", color="primary")
        return dbc.Alert([
            html.H6("👤 User Information", className="mb-2"),
            html.P([
                html.Strong("Username: "), user['username'], html.Br(),
                html.Strong("Email: "), user['email'], html.Br(),
                html.Strong("Role: "), role_badge
            ])
        ], color="light")
    return "No user data"

# Chat callback
@app.callback(
    [Output("chat-messages", "children"),
     Output("chat-input", "value")],
    [Input("send-btn", "n_clicks")],
    [State("chat-input", "value")],
    prevent_initial_call=True
)
def handle_chat(n_clicks, message):
    if not n_clicks or not message:
        raise PreventUpdate
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    
    if not token:
        return "Please login first", ""
    
    # Send message to backend
    headers = {"Authorization": f"Bearer {token}"}
    data = {"question": message}
    
    try:
        response = requests.post("http://localhost:8000/query", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Create chat message display
            messages = [
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            html.Strong("You: "), message
                        ])
                    ])
                ], className="mb-2", color="primary", outline=True),
                
                dbc.Card([
                    dbc.CardBody([
                        html.P([
                            html.Strong("Orbitbot: "), result['answer']
                        ])
                    ])
                ], className="mb-2", color="light", outline=True)
            ]
            
            return messages, ""
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            return [dbc.Alert(error_msg, color="danger")], message
            
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        return [dbc.Alert(error_msg, color="danger")], message

# Upload callback
@app.callback(
    Output('upload-output', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def handle_upload(contents, filename):
    if not contents:
        return ""
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    user = dash_session_manager.get_current_user(session_id)
    
    if not token or user['role'] != 'admin':
        return dbc.Alert("Admin access required", color="danger")
    
    try:
        # Decode the file content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Prepare file for upload
        files = {'file': (filename, io.BytesIO(decoded), 'application/octet-stream')}
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post("http://localhost:8000/upload", files=files, headers=headers)
        
        if response.status_code == 200:
            return dbc.Alert(f"✅ File '{filename}' uploaded successfully!", color="success")
        else:
            return dbc.Alert(f"❌ Upload failed: {response.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"❌ Upload error: {str(e)}", color="danger")

# Document list callback
@app.callback(
    Output("document-list", "children"),
    [Input("main-tabs", "active_tab")],
    prevent_initial_call=True
)
def update_document_list(active_tab):
    if active_tab != "documents-tab":
        raise PreventUpdate
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    user = dash_session_manager.get_current_user(session_id)
    
    if not token or user['role'] != 'admin':
        return dbc.Alert("Admin access required", color="danger")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/documents", headers=headers)
        
        if response.status_code == 200:
            documents = response.json()
            
            if not documents:
                return dbc.Alert("No documents uploaded yet", color="info")
            
            table_data = []
            for doc in documents:
                table_data.append({
                    "ID": doc['id'],
                    "Filename": doc['filename'],
                    "Type": doc['file_type'],
                    "Size": f"{doc['file_size']} bytes",
                    "Uploaded": doc['created_at'][:10],
                    "Status": "Processed" if doc['processed'] else "Processing"
                })
            
            return dash_table.DataTable(
                data=table_data,
                columns=[{"name": i, "id": i} for i in table_data[0].keys()],
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': '#0000fe', 'color': 'white', 'fontWeight': 'bold'}
            )
        else:
            return dbc.Alert(f"Error loading documents: {response.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Create user callback
@app.callback(
    Output("create-user-output", "children"),
    [Input("create-user-btn", "n_clicks")],
    [State("new-user-username", "value"),
     State("new-user-email", "value"),
     State("new-user-password", "value"),
     State("new-user-role", "value")],
    prevent_initial_call=True
)
def create_user(n_clicks, username, email, password, role):
    if not n_clicks:
        raise PreventUpdate
    
    if not all([username, email, password]):
        return dbc.Alert("Please fill in all required fields", color="warning")
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    user = dash_session_manager.get_current_user(session_id)
    
    if not token or user['role'] != 'admin':
        return dbc.Alert("Admin access required", color="danger")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        
        response = requests.post("http://localhost:8000/auth/users/create", json=data, headers=headers)
        
        if response.status_code == 200:
            return dbc.Alert(f"✅ User '{username}' created successfully!", color="success")
        else:
            return dbc.Alert(f"❌ Failed to create user: {response.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger")

# User list callback
@app.callback(
    Output("user-list", "children"),
    [Input("main-tabs", "active_tab")],
    prevent_initial_call=True
)
def update_user_list(active_tab):
    if active_tab != "users-tab":
        raise PreventUpdate
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    user = dash_session_manager.get_current_user(session_id)
    
    if not token or user['role'] != 'admin':
        return dbc.Alert("Admin access required", color="danger")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/auth/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            
            if not users:
                return dbc.Alert("No users found", color="info")
            
            table_data = []
            for user_data in users:
                table_data.append({
                    "ID": user_data['id'],
                    "Username": user_data['username'],
                    "Email": user_data['email'],
                    "Role": user_data['role'],
                    "Active": "Yes" if user_data['is_active'] else "No",
                    "Created": user_data['created_at'][:10]
                })
            
            return dash_table.DataTable(
                data=table_data,
                columns=[{"name": i, "id": i} for i in table_data[0].keys()],
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': '#0000fe', 'color': 'white', 'fontWeight': 'bold'}
            )
        else:
            return dbc.Alert(f"Error loading users: {response.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Analytics callback
@app.callback(
    Output("analytics-content", "children"),
    [Input("main-tabs", "active_tab")],
    prevent_initial_call=True
)
def update_analytics(active_tab):
    if active_tab != "analytics-tab":
        raise PreventUpdate
    
    session_id = get_session_id()
    token = dash_session_manager.get_session(session_id, "token")
    user = dash_session_manager.get_current_user(session_id)
    
    if not token or user['role'] != 'admin':
        return dbc.Alert("Admin access required", color="danger")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/analytics/stats", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            
            # Create analytics cards
            cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(stats['total_users'], className="text-primary"),
                            html.P("Total Users", className="mb-0")
                        ])
                    ], color="light", outline=True)
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(stats['total_documents'], className="text-success"),
                            html.P("Total Documents", className="mb-0")
                        ])
                    ], color="light", outline=True)
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(len(stats['search_stats']), className="text-info"),
                            html.P("Search Queries", className="mb-0")
                        ])
                    ], color="light", outline=True)
                ], width=4)
            ], className="mb-4")
            
            return cards
        else:
            return dbc.Alert(f"Error loading analytics: {response.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

if __name__ == "__main__":
    print("🚀 Starting Enhanced SKF Orbitbot Dash Application...")
    print("📱 Dashboard will be available at: http://localhost:8052")
    print("🔧 Backend API should be running at: http://localhost:8000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=8052)
