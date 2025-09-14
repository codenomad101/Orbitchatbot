# SKF Orbitbot React Frontend

A modern React frontend for the SKF Orbitbot AI Document Assistant, built with TypeScript, Material-UI, and React Router.

## Features

- 🔐 **Authentication System**: Login/Register with JWT tokens
- 👥 **Role-based Access**: User and Admin roles with different permissions
- 💬 **Chat Interface**: Interactive chat with the AI assistant
- 📄 **Document Management**: Upload and manage documents (Admin only)
- 👤 **User Management**: Create, update, and manage users (Admin only)
- 📊 **Analytics Dashboard**: System statistics and usage analytics (Admin only)
- 🔍 **Search History**: View recent search queries
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 19** with TypeScript
- **Material-UI (MUI)** for UI components
- **React Router** for navigation
- **Axios** for API communication
- **Recharts** for analytics charts
- **React Dropzone** for file uploads

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd react-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

### Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── ProtectedRoute.tsx # Route protection
│   ├── LoadingSpinner.tsx # Loading component
│   └── ErrorBoundary.tsx  # Error handling
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── pages/              # Page components
│   ├── Login.tsx       # Login page
│   ├── Register.tsx    # Registration page
│   ├── Dashboard.tsx   # Chat interface
│   ├── Documents.tsx   # Document management
│   ├── Users.tsx       # User management
│   └── Analytics.tsx   # Analytics dashboard
└── App.tsx            # Main app component
```

## API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /auth/users` - List users (Admin only)
- `POST /auth/users/create` - Create user (Admin only)
- `PUT /auth/users/{id}/role` - Update user role (Admin only)
- `PUT /auth/users/{id}/deactivate` - Deactivate user (Admin only)
- `POST /upload` - Upload documents (Admin only)
- `GET /documents` - List documents (Admin only)
- `DELETE /documents/{id}` - Delete document (Admin only)
- `POST /query` - Chat with AI assistant
- `GET /search/history` - Get search history
- `GET /analytics/stats` - Get analytics data (Admin only)

## Features by Role

### User Role
- Chat with AI assistant
- View search history
- Access to dashboard

### Admin Role
- All user features
- Document upload and management
- User management (create, update, deactivate)
- Analytics dashboard
- System logs

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Deployment

1. Build the project:
   ```bash
   npm run build
   ```

2. The built files will be in the `dist/` directory

3. Serve the static files using any web server (nginx, Apache, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the SKF Orbitbot system.