import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Avatar,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { 
  Send as SendIcon, 
  SmartToy as BotIcon, 
  Person as PersonIcon,
  History as HistoryIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  sources?: Array<{
    title: string;
    content: string;
    score: number;
  }>;
}

interface SearchHistoryItem {
  id: number;
  query: string;
  answer: string;
  created_at: string;
  response_time_ms: number;
}

interface DashboardProps {
  sidebarOpen?: boolean;
  sidebarWidth?: number;
}

const Dashboard: React.FC<DashboardProps> = ({ sidebarOpen = false, sidebarWidth = 280 }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const response = await axios.get('/search/history?limit=10');
      setSearchHistory(response.data);
    } catch (err: any) {
      console.error('Failed to fetch search history:', err);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post('/query', {
        question: inputMessage,
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.answer,
        sender: 'bot',
        timestamp: new Date(),
        sources: response.data.sources,
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Refresh search history after successful query
      fetchSearchHistory();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get response from AI');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message: Message) => (
    <Box
      key={message.id}
      sx={{
        display: 'flex',
        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          maxWidth: '70%',
          flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
        }}
      >
        <Avatar
          sx={{
            bgcolor: message.sender === 'user' ? '#0000fe' : '#1976d2',
            mx: 1,
            width: 32,
            height: 32,
          }}
        >
          {message.sender === 'user' ? <PersonIcon /> : <BotIcon />}
        </Avatar>
        
        <Paper
          elevation={1}
          sx={{
            p: 2,
            backgroundColor: message.sender === 'user' ? '#0000fe' : '#f5f5f5',
            color: message.sender === 'user' ? 'white' : 'black',
            borderRadius: 2,
          }}
        >
          <Typography variant="body1">{message.text}</Typography>
          
          {message.sources && message.sources.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Sources:
              </Typography>
              {message.sources.slice(0, 3).map((source, index) => (
                <Chip
                  key={index}
                  label={`${source.title || 'Unknown Source'} (${Math.round((source.score || 0) * 100)}%)`}
                  size="small"
                  sx={{ mr: 0.5, mt: 0.5, fontSize: '0.7rem' }}
                  color="secondary"
                />
              ))}
            </Box>
          )}
          
          <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
            {message.timestamp.toLocaleTimeString()}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: sidebarOpen ? sidebarWidth : 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#ffffff',
        transition: 'left 0.3s ease-in-out',
        zIndex: 1,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Typography variant="h5" sx={{ color: '#0000fe', fontWeight: 'bold' }}>
          🤖 SKF Orbitbot
        </Typography>
      </Box>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#ffffff',
          minHeight: 0, // Important for flex overflow
        }}
      >
        <Box sx={{ 
          width: '100%', 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          px: { xs: 1, sm: 2, md: 3, lg: 4 },
          py: 2,
        }}>
          {messages.length === 0 && (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
                py: 5,
               }}
            >
              <BotIcon sx={{ fontSize: 80, color: '#0000fe', mb: 3 }} />
              <Typography variant="h4" sx={{ color: '#0000fe', fontWeight: 'bold', mb: 2 }}>
                How can I help you today?
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
                Ask me anything about your documents. I can help you find information, 
                summarize content, answer questions, and provide insights.
              </Typography>
              
              {/* Quick suggestions */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center', maxWidth: 800 }}>
                {[
                  "What documents do we have?",
                  "Summarize the latest report",
                  "Find information about...",
                  "Explain the key points"
                ].map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    onClick={() => setInputMessage(suggestion)}
                    sx={{
                      borderColor: '#e0e0e0',
                      color: '#666',
                      textTransform: 'none',
                      borderRadius: 3,
                      px: 3,
                      py: 1,
                      '&:hover': {
                        borderColor: '#0000fe',
                        backgroundColor: '#f0f0ff',
                      },
                    }}
                  >
                    {suggestion}
                  </Button>
                ))}
              </Box>
            </Box>
          )}

          {messages.length > 0 && (
            <Box sx={{ 
              flex: 1, 
              overflow: 'auto', 
              py: 2,
              display: 'flex',
              flexDirection: 'column',
            }}>
              <Box sx={{ 
                maxWidth: { xs: '100%', sm: '90%', md: '80%', lg: '70%' }, 
                mx: 'auto', 
                width: '100%',
                flex: 1,
              }}>
                {messages.map(renderMessage)}

                {isLoading && (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'flex-start',
                      mb: 2,
                    }}
                  >
                    <Avatar sx={{ bgcolor: '#1976d2', mx: 1, width: 32, height: 32 }}>
                      <BotIcon />
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        backgroundColor: '#f5f5f5',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        Orbitbot is thinking...
                      </Typography>
                    </Paper>
                  </Box>
                )}
              </Box>
              <div ref={messagesEndRef} />
            </Box>
          )}

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mb: 2, maxWidth: { xs: '100%', sm: '90%', md: '80%', lg: '70%' }, mx: 'auto', width: '100%' }}>
              {error}
            </Alert>
          )}
        </Box>
      </Box>

      {/* Input Area - Fixed at bottom */}
      <Box
        sx={{
          p: 3,
          borderTop: '1px solid #e0e0e0',
          backgroundColor: '#ffffff',
          flexShrink: 0,
        }}
      >
        <Box sx={{ 
          width: '100%',
          maxWidth: { xs: '100%', sm: '90%', md: '80%', lg: '70%' }, 
          mx: 'auto',
        }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Message Orbitbot..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: '#f8f9fa',
                  '&:hover': {
                    backgroundColor: '#f0f0f0',
                  },
                  '&.Mui-focused': {
                    backgroundColor: '#ffffff',
                  },
                },
                '& .MuiOutlinedInput-input': {
                  py: 1.5,
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{
                backgroundColor: '#0000fe',
                '&:hover': {
                  backgroundColor: '#0000cc',
                },
                minWidth: 48,
                height: 48,
                borderRadius: '50%',
                p: 0,
              }}
            >
              <SendIcon />
            </Button>
          </Box>
          
          {/* Search History - Collapsible */}
          {searchHistory && searchHistory.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Accordion sx={{ boxShadow: 'none', '&:before': { display: 'none' } }}>
                <AccordionSummary 
                  expandIcon={<ExpandMoreIcon />}
                  sx={{ 
                    minHeight: 'auto',
                    '& .MuiAccordionSummary-content': { margin: '8px 0' }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <HistoryIcon sx={{ mr: 1, color: '#666', fontSize: 20 }} />
                    <Typography variant="body2" color="text.secondary">
                      Recent searches
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {searchHistory && searchHistory.length > 0 ? searchHistory.slice(0, 5).map((item) => (
                      <Button
                        key={item.id}
                        variant="outlined"
                        size="small"
                        onClick={() => setInputMessage(item.query || '')}
                        sx={{
                          borderColor: '#e0e0e0',
                          color: '#666',
                          textTransform: 'none',
                          borderRadius: 2,
                          fontSize: '0.75rem',
                          '&:hover': {
                            borderColor: '#0000fe',
                            backgroundColor: '#f0f0ff',
                          },
                        }}
                      >
                        {item.query && item.query.length > 30 ? `${item.query.substring(0, 30)}...` : item.query || 'Unknown query'}
                      </Button>
                    )) : (
                      <Typography variant="body2" color="text.secondary">
                        No recent searches
                      </Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;