import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Alert,
} from '@mui/material';
import {
  People as PeopleIcon,
  Folder as FolderIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

interface AnalyticsData {
  total_users: number;
  total_documents: number;
  search_stats: Array<{
    date: string;
    count: number;
  }>;
  vector_store_stats: {
    total_vectors: number;
    total_chunks: number;
  };
}

const COLORS = ['#0000fe', '#1976d2', '#42a5f5', '#90caf9'];

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin) {
      fetchAnalytics();
    }
  }, [isAdmin]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/analytics/stats');
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">
          Admin access required to view analytics.
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <LoadingSpinner message="Loading analytics data..." />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const pieData = [
    { name: 'Users', value: data?.total_users || 0 },
    { name: 'Documents', value: data?.total_documents || 0 },
    { name: 'Vectors', value: data?.vector_store_stats?.total_vectors || 0 },
    { name: 'Chunks', value: data?.vector_store_stats?.total_chunks || 0 },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ color: '#0000fe', fontWeight: 'bold' }}>
        📊 Analytics Dashboard
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 5 }}>
        System overview and usage statistics
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={4} sx={{ mb: 5 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PeopleIcon sx={{ fontSize: 48, color: '#0000fe', mr: 3 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Users
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                    {data?.total_users || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <FolderIcon sx={{ fontSize: 48, color: '#1976d2', mr: 3 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Documents
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                    {data?.total_documents || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SearchIcon sx={{ fontSize: 48, color: '#42a5f5', mr: 3 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Queries
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                    {data?.search_stats?.reduce((acc, stat) => acc + stat.count, 0) || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 48, color: '#90caf9', mr: 3 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Vector Chunks
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                    {data?.vector_store_stats?.total_chunks || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={4}>
        {/* Search Activity Chart */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 4, borderRadius: 3, boxShadow: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              📈 Search Activity
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data?.search_stats || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#0000fe"
                    strokeWidth={3}
                    name="Search Queries"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* System Overview Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 4, borderRadius: 3, boxShadow: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              🥧 System Overview
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Vector Store Statistics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 4, borderRadius: 3, boxShadow: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
              🗄️ Vector Store Statistics
            </Typography>
            <Grid container spacing={4}>
              <Grid item xs={12} sm={6}>
                <Box sx={{ textAlign: 'center', p: 4 }}>
                  <Typography variant="h2" color="primary" sx={{ fontWeight: 'bold' }}>
                    {data?.vector_store_stats?.total_vectors || 0}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    Total Vectors
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ textAlign: 'center', p: 4 }}>
                  <Typography variant="h2" color="secondary" sx={{ fontWeight: 'bold' }}>
                    {data?.vector_store_stats?.total_chunks || 0}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    Document Chunks
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Analytics;

