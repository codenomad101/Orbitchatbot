import dash
from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import requests
from auth_components_dash import AuthManager, dash_session_manager

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "SKF Orbitbot - Simple Version"

def get_session_id():
    return "default_session"

# Simple auth layout
def create_auth_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H1("🤖 SKF Orbitbot", className="text-center", style={"color": "#0000fe"})
                    ]),
                    dbc.CardBody([
                        dbc.InputGroup([
                            dbc.InputGroupText("👤"),
                            dbc.Input(id="username", placeholder="Username", value="admin")
                        ], className="mb-3"),
                        
                        dbc.InputGroup([
                            dbc.InputGroupText("🔒"),
                            dbc.Input(id="password", placeholder="Password", type="password", value="admin123")
                        ], className="mb-3"),
                        
                        dbc.Button("Login", id="login-btn", color="primary", className="w-100 mb-3", size="lg"),
                        
                        dbc.Alert(id="alert", is_open=False)
                    ])
                ])
            ], width=6)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True)

# Simple main layout
def create_main_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🎉 Welcome to SKF Orbitbot!", className="text-center mb-4"),
                html.Div([
                    html.P("You are successfully logged in!", className="text-center"),
                    html.P(id="user-info", className="text-center"),
                    dbc.Button("Logout", id="logout-btn", color="danger", className="mt-3")
                ])
            ])
        ])
    ], className="min-vh-100 d-flex align-items-center justify-content-center")

# App layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Main page callback
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
    prevent_initial_call=False
)
def display_page(pathname):
    session_id = get_session_id()
    print(f"DEBUG: Checking authentication for session {session_id}")
    print(f"DEBUG: Session data: {dash_session_manager.sessions}")
    
    if dash_session_manager.is_authenticated(session_id):
        print("DEBUG: User is authenticated, showing main layout")
        return create_main_layout()
    else:
        print("DEBUG: User is not authenticated, showing auth layout")
        return create_auth_layout()

# Login callback
@app.callback(
    [Output("alert", "children"),
     Output("alert", "is_open"),
     Output("alert", "color"),
     Output("page-content", "children", allow_duplicate=True)],
    [Input("login-btn", "n_clicks")],
    [State("username", "value"),
     State("password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    print(f"DEBUG: Login button clicked with username: {username}")
    
    if not n_clicks:
        raise PreventUpdate
    
    if not username or not password:
        return "Please fill in all fields", True, "danger", no_update
    
    # Test login
    auth_manager = AuthManager()
    result = auth_manager.login(username, password)
    
    if result:
        print("DEBUG: Login successful, setting session")
        session_id = get_session_id()
        dash_session_manager.set_session(session_id, "authenticated", True)
        dash_session_manager.set_session(session_id, "user", result["user"])
        dash_session_manager.set_session(session_id, "token", result["access_token"])
        
        print(f"DEBUG: Session set: {dash_session_manager.sessions}")
        return "Login successful!", True, "success", create_main_layout()
    else:
        print("DEBUG: Login failed")
        return "Invalid credentials", True, "danger", no_update

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
        print("DEBUG: Logout successful, session cleared")
        return create_auth_layout()
    raise PreventUpdate

# User info callback
@app.callback(
    Output("user-info", "children"),
    [Input("page-content", "children")],
    prevent_initial_call=True
)
def update_user_info(children):
    session_id = get_session_id()
    user = dash_session_manager.get_current_user(session_id)
    
    if user:
        return f"Logged in as: {user['username']} ({user['role']})"
    return "No user data"

if __name__ == "__main__":
    print("🚀 Starting Simple Dash App...")
    app.run(debug=True, host="0.0.0.0", port=8051)


