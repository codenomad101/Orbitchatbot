# 🚀 SKF Orbitbot React Frontend

## 🎯 Overview
Modern React frontend for the SKF Orbitbot AI Document Assistant with Material-UI components and full admin functionality.

## ✨ Features

### 🔐 Authentication
- **Login/Register** with JWT tokens
- **Role-based access control** (Admin/User)
- **Persistent sessions** with localStorage
- **Protected routes** for admin features

### 💬 Chat Interface
- **Real-time chat** with AI assistant
- **Loading indicators** with "Orbitbot is thinking..."
- **Message history** with timestamps
- **Source citations** from documents
- **Responsive design** for mobile/desktop

### 👑 Admin Features
- **Document Management**
  - Drag & drop file upload
  - Support for PDF, DOCX, TXT
  - Document processing status
  - Delete documents
  - File size formatting

- **User Management**
  - Create new users
  - Change user roles (Admin/User)
  - Activate/Deactivate users
  - User activity tracking

- **Analytics Dashboard**
  - System statistics
  - Search activity charts
  - Vector store metrics
  - Interactive charts with Recharts

### 🎨 UI/UX
- **Material-UI** components
- **Blue theme** (#0000fe primary color)
- **Responsive design**
- **Loading states** and error handling
- **Professional navigation** with sidebar

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Material-UI** for components
- **React Router** for navigation
- **Axios** for API calls
- **Recharts** for analytics
- **React Dropzone** for file uploads

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- Backend API running on port 8000

### Installation
```bash
cd react-frontend
npm install
```

### Development
```bash
npm run dev
# or
npm start
```

### Build for Production
```bash
npm run build
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000 (or http://localhost:5173)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔑 Default Admin Credentials

- **Username**: admin
- **Password**: admin123

## 📁 Project Structure

```
react-frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx          # Main layout with navigation
│   │   └── ProtectedRoute.tsx  # Route protection
│   ├── contexts/
│   │   └── AuthContext.tsx     # Authentication state
│   ├── pages/
│   │   ├── Login.tsx           # Login page
│   │   ├── Register.tsx        # Registration page
│   │   ├── Dashboard.tsx       # Chat interface
│   │   ├── Documents.tsx       # Document management
│   │   ├── Users.tsx           # User management
│   │   └── Analytics.tsx       # Analytics dashboard
│   ├── App.tsx                 # Main app component
│   └── main.tsx               # App entry point
├── package.json
└── README.md
```

## 🔧 Configuration

### API Base URL
The API base URL is configured in `src/contexts/AuthContext.tsx`:
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

### Theme Colors
Primary color is set to `#0000fe` (blue) throughout the application.

## 🎯 Key Features Implemented

✅ **Authentication System**
- JWT token management
- Role-based access control
- Persistent login sessions

✅ **Chat Interface**
- Real-time messaging
- Loading indicators
- Source citations
- Message history

✅ **Admin Dashboard**
- Document upload/management
- User management
- Analytics with charts
- Responsive design

✅ **Modern UI/UX**
- Material-UI components
- Professional styling
- Mobile responsive
- Error handling

## 🚀 Next Steps

1. **Start the React app**: `npm run dev`
2. **Access**: http://localhost:3000
3. **Login** with admin credentials
4. **Upload documents** and start chatting!

## 🔄 Migration from Dash

This React frontend replaces the previous Dash implementation with:
- ✅ Better performance
- ✅ Modern UI components
- ✅ No layout ID errors
- ✅ Smooth loading states
- ✅ Professional design
- ✅ Mobile responsive


