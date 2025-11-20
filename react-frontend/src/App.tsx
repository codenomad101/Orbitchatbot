import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { CssBaseline, Box } from "@mui/material";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import ErrorBoundary from "./components/ErrorBoundary";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ChatHistory from "./pages/ChatHistory";
import KnowledgeHub from "./pages/KnowledgeHub";
import CodingHub from "./pages/CodingHub";
import Onboarding from "./pages/Onboarding";
import AwsSolutions from "./pages/AwsSolutions";
import Documents from "./pages/Documents";
import Users from "./pages/Users";
import Analytics from "./pages/Analytics";
import FormattingTest from "./pages/FormattingTest";

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: "#0000fe",
    },
    secondary: {
      main: "#1976d2",
    },
    background: {
      default: "#f5f5f5",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <AuthProvider>
          <Router>
            <Box sx={{ minHeight: "100vh" }}>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="chat-history" element={<ChatHistory />} />
                  <Route path="dashboard" element={<Dashboard />} />
                  <Route path="knowledge-hub" element={<KnowledgeHub />} />
                  <Route path="coding-hub" element={<CodingHub />} />
                  <Route path="onboarding" element={<Onboarding />} />
                  <Route path="aws-solutions" element={<AwsSolutions />} />
                  <Route path="documents" element={<Documents />} />
                  <Route path="users" element={<Users />} />
                  <Route path="analytics" element={<Analytics />} />
                  <Route path="formatting-test" element={<FormattingTest />} />
                </Route>

                {/* Catch all route */}
                <Route
                  path="*"
                  element={<Navigate to="/dashboard" replace />}
                />
              </Routes>
            </Box>
          </Router>
        </AuthProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
