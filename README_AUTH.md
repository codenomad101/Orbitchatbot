# SKF Orbitbot - AI Document Assistant with Authentication

## 🔐 Authentication System Overview

This application now includes a comprehensive JWT-based authentication system with role-based access control. The system supports both **Admin** and **User** roles with different levels of access.

## 🚀 Features

### Authentication Features
- **JWT-based authentication** with secure token management
- **User registration and login** with email validation
- **Role-based access control** (Admin vs User)
- **Session management** with automatic token refresh
- **Password hashing** using bcrypt for security

### Admin Features
- **File upload and management** - Upload PDF, DOCX, TXT files
- **Document library management** - View, delete documents
- **User management** - View all users, deactivate accounts
- **Full access** to all application features

### User Features
- **Chat interface** - Ask questions about uploaded documents
- **View source references** - See which documents were used for answers
- **Limited access** - Cannot upload or manage documents

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r ../requirements.txt

# Install frontend dependencies (if using virtual environment)
cd ../frontend
pip install streamlit
```

### 2. Backend Setup

```bash
cd backend
python app.py
```

The backend will start on `http://127.0.0.1:8000`

### 3. Frontend Setup

```bash
cd frontend
streamlit run streamlit_app.py
```

The frontend will start on `http://localhost:8501`

## 👤 Default Admin Account

**Username:** `admin`  
**Password:** `admin123`

⚠️ **Important:** Change the default admin password after first login for security!

## 🔧 Configuration

### Environment Variables

You can set the following environment variables for customization:

```bash
export SECRET_KEY="your-secret-key-here"
export ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### User Data Storage

User data is stored in `backend/data/users.json`. This file is automatically created with a default admin user on first run.

## 📁 Project Structure

```
indbot/
├── backend/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── auth_handler.py      # JWT and password handling
│   │   ├── models.py            # Pydantic models
│   │   └── dependencies.py      # FastAPI dependencies
│   ├── app.py                   # Main FastAPI application
│   └── data/
│       └── users.json           # User data storage
├── frontend/
│   ├── streamlit_app.py         # Main entry point
│   ├── streamlit_app_auth.py    # Authenticated application
│   └── auth_components.py       # Authentication components
└── requirements.txt             # Dependencies
```

## 🔐 Security Features

### Password Security
- Passwords are hashed using bcrypt
- Minimum password length enforcement
- Secure password verification

### JWT Security
- Tokens expire after 24 hours by default
- Secure token generation and verification
- Automatic token refresh handling

### Access Control
- Role-based permissions
- Protected API endpoints
- Admin-only features properly secured

## 🎨 UI/UX Improvements

### Professional Design
- Modern gradient backgrounds
- Clean card-based layout
- Responsive design elements
- Professional color scheme

### User Experience
- Intuitive login/register flow
- Clear role indicators
- Helpful error messages
- Smooth animations and transitions

### Role-based Interface
- Different sidebar content for Admin vs User
- Clear access level indicators
- Appropriate feature visibility

## 📋 API Endpoints

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `GET /auth/users` - List all users (Admin only)
- `PUT /auth/users/{username}/role` - Update user role (Admin only)
- `PUT /auth/users/{username}/deactivate` - Deactivate user (Admin only)

### Protected Endpoints
- `POST /upload` - Upload documents (Admin only)
- `GET /documents` - List documents (Admin only)
- `DELETE /documents/{filename}` - Delete document (Admin only)
- `POST /query` - Query documents (Authenticated users)

## 🔄 Usage Flow

### For Admins
1. Login with admin credentials
2. Upload documents via sidebar
3. Manage document library
4. Manage user accounts
5. Chat with AI assistant

### For Users
1. Register new account or login
2. Chat with AI assistant
3. View source references in responses
4. Cannot upload or manage documents

## 🛡️ Security Best Practices

1. **Change default passwords** immediately after setup
2. **Use strong passwords** for all accounts
3. **Regularly review user accounts** and deactivate unused ones
4. **Monitor system logs** for suspicious activity
5. **Keep dependencies updated** for security patches

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if port 8000 is available
   - Ensure all dependencies are installed
   - Check Python version compatibility

2. **Authentication errors**
   - Verify backend is running
   - Check network connectivity
   - Clear browser cache and cookies

3. **File upload issues**
   - Ensure you're logged in as admin
   - Check file size limits
   - Verify supported file formats

### Support

For issues or questions:
1. Check the console logs for error messages
2. Verify all services are running
3. Check network connectivity between frontend and backend

## 🚀 Future Enhancements

Potential improvements for the authentication system:
- Email verification for registration
- Password reset functionality
- Two-factor authentication
- Audit logging for admin actions
- User profile management
- Session timeout warnings

