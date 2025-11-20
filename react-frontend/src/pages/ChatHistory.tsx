import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Search as SearchIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import FormattedText from '../components/FormattedText';

interface SearchHistoryItem {
  id: number;
  query: string;
  answer: string;
  created_at: string;
  response_time_ms: number;
}

const ChatHistory: React.FC = () => {
  const navigate = useNavigate();
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAllSearchHistory();
  }, []);

  const fetchAllSearchHistory = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/search/history?limit=100'); // Get more history
      setSearchHistory(response.data);
    } catch (err: any) {
      console.error('Failed to fetch search history:', err);
      setError('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
  };

  const groupHistoryByDate = (history: SearchHistoryItem[]) => {
    const groups: { [key: string]: SearchHistoryItem[] } = {};
    
    history.forEach(item => {
      const date = new Date(item.created_at);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      let groupKey: string;
      if (date.toDateString() === today.toDateString()) {
        groupKey = 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        groupKey = 'Yesterday';
      } else {
        groupKey = date.toLocaleDateString([], { month: 'long', day: 'numeric', year: 'numeric' });
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
    });
    
    return groups;
  };

  const renderHistoryItem = (item: SearchHistoryItem) => (
    <Card
      key={item.id}
      sx={{
        mb: 2,
        border: '1px solid #e0e0e0',
        borderRadius: 2,
        transition: 'all 0.2s ease',
        '&:hover': {
          borderColor: '#0000fe',
          boxShadow: '0 2px 8px rgba(0, 0, 254, 0.1)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Question */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: '#0000fe',
              width: 32,
              height: 32,
              mr: 2,
              flexShrink: 0,
            }}
          >
            <PersonIcon sx={{ fontSize: 18 }} />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 500,
                color: '#333',
                lineHeight: 1.4,
                mb: 1,
              }}
            >
              {item.query || 'Unknown query'}
            </Typography>
          </Box>
        </Box>

        {/* Answer */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: '#f0f0f0',
              width: 32,
              height: 32,
              mr: 2,
              flexShrink: 0,
            }}
          >
            <BotIcon sx={{ fontSize: 18, color: '#666' }} />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ 
              maxHeight: '200px',
              overflow: 'hidden',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: '20px',
                background: 'linear-gradient(transparent, white)',
                pointerEvents: 'none',
              }
            }}>
              <FormattedText 
                text={item.answer || 'No answer available'}
                variant="body2"
                color="#666"
              />
            </Box>
          </Box>
        </Box>

        {/* Metadata */}
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {item.response_time_ms && (
              <Chip
                icon={<ScheduleIcon />}
                label={`${item.response_time_ms}ms`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem' }}
              />
            )}
            <Typography variant="caption" color="text.secondary">
              {formatDate(item.created_at)}
            </Typography>
          </Box>
          <Button
            size="small"
            variant="outlined"
            onClick={() => navigate('/dashboard')}
            sx={{
              fontSize: '0.75rem',
              textTransform: 'none',
              borderColor: '#0000fe',
              color: '#0000fe',
              '&:hover': {
                backgroundColor: '#f0f0ff',
                borderColor: '#0000cc',
              },
            }}
          >
            View Full Chat
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          p: 3,
        }}
      >
        <CircularProgress size={60} sx={{ mb: 3 }} />
        <Typography variant="h6" color="text.secondary">
          Loading chat history...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={handleBackToDashboard}
          sx={{ backgroundColor: '#0000fe' }}
        >
          Back to Dashboard
        </Button>
      </Box>
    );
  }

  const groupedHistory = groupHistoryByDate(searchHistory);

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <Box
        sx={{
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e0e0e0',
          p: 2,
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              onClick={handleBackToDashboard}
              sx={{
                mr: 2,
                color: '#0000fe',
                '&:hover': {
                  backgroundColor: '#f0f0ff',
                },
              }}
            >
              <ArrowBackIcon />
            </IconButton>
            <HistoryIcon sx={{ fontSize: 32, color: '#0000fe', mr: 2 }} />
            <Typography variant="h4" sx={{ color: '#0000fe', fontWeight: 'bold' }}>
              Chat History
            </Typography>
          </Box>
          <Chip
            icon={<SearchIcon />}
            label={`${searchHistory.length} conversations`}
            color="primary"
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ p: 3 }}>
        {searchHistory.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 8,
              textAlign: 'center',
            }}
          >
            <HistoryIcon sx={{ fontSize: 80, color: '#ccc', mb: 3 }} />
            <Typography variant="h5" color="text.secondary" sx={{ mb: 2 }}>
              No chat history yet
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Start a conversation to see your chat history here
            </Typography>
            <Button
              variant="contained"
              onClick={handleBackToDashboard}
              sx={{ backgroundColor: '#0000fe' }}
            >
              Start Chatting
            </Button>
          </Box>
        ) : (
          <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            {Object.entries(groupedHistory).map(([dateGroup, items]) => (
              <Box key={dateGroup} sx={{ mb: 4 }}>
                <Typography
                  variant="h6"
                  sx={{
                    color: '#0000fe',
                    fontWeight: 'bold',
                    mb: 2,
                    pb: 1,
                    borderBottom: '2px solid #0000fe',
                    display: 'inline-block',
                  }}
                >
                  {dateGroup}
                </Typography>
                {items.map(renderHistoryItem)}
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ChatHistory;
