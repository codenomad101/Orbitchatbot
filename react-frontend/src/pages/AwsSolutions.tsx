import React, { useState, useRef, useEffect } from 'react';
import {
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
  IconButton,
  Tooltip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { 
  Send as SendIcon, 
  SmartToy as BotIcon, 
  Person as PersonIcon,
  History as HistoryIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Cloud as CloudIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import axios from 'axios';
import FormattedText from '../components/FormattedText';

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
  intent?: string;
}

interface SearchHistoryItem {
  id: number;
  query: string;
  answer: string;
  created_at: string;
  response_time_ms: number;
}

interface AwsSolutionsProps {
  sidebarOpen?: boolean;
  sidebarWidth?: number;
}

const AwsSolutions: React.FC<AwsSolutionsProps> = ({ sidebarOpen = false, sidebarWidth = 280 }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [recentSearchesExpanded, setRecentSearchesExpanded] = useState(false);
  const [visibleSources, setVisibleSources] = useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleSourceVisibility = (messageId: string) => {
    setVisibleSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  const addHistoryToChat = (item: SearchHistoryItem) => {
    setRecentSearchesExpanded(false);
    
    const existingUserMessage = messages.find(msg => msg.id === `history-${item.id}-user`);
    if (existingUserMessage) {
      const messageElement = document.getElementById(`message-${existingUserMessage.id}`);
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    const userMessage: Message = {
      id: `history-${item.id}-user`,
      text: item.query || '',
      sender: 'user',
      timestamp: new Date(item.created_at),
    };
    
    const botMessage: Message = {
      id: `history-${item.id}-bot`,
      text: item.answer || '',
      sender: 'bot',
      timestamp: new Date(item.created_at),
    };
    
    setMessages(prev => [...prev, userMessage, botMessage]);
    
    setTimeout(() => {
      const messageElement = document.getElementById(`message-${userMessage.id}`);
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
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
        intent: response.data.intent,
      };

      setMessages(prev => [...prev, botMessage]);
      
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

  const renderMessage = (message: Message) => {
    const isHistorical = message.id.startsWith('history-');
    
    return (
      <Box
        key={message.id}
        id={`message-${message.id}`}
        sx={{
          display: 'flex',
          justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
          mb: 2,
          opacity: isHistorical ? 0.8 : 1,
          position: 'relative',
        }}
      >
        {isHistorical && (
          <Box
            sx={{
              position: 'absolute',
              top: -8,
              left: message.sender === 'user' ? 'auto' : 0,
              right: message.sender === 'user' ? 0 : 'auto',
              backgroundColor: '#e3f2fd',
              color: '#1976d2',
              px: 1,
              py: 0.5,
              borderRadius: 1,
              fontSize: '0.7rem',
              fontWeight: 'bold',
              zIndex: 1,
            }}
          >
            📚 From History
          </Box>
        )}
        
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-start',
            maxWidth: '70%',
            flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
            mt: isHistorical ? 2 : 0,
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
              border: isHistorical ? '2px dashed #e0e0e0' : 'none',
            }}
          >
            <FormattedText 
              text={message.text} 
              variant="body1"
              color={message.sender === 'user' ? 'white' : 'black'}
            />
          
          {message.sources && message.sources.length > 0 && (
            <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title={visibleSources.has(message.id) ? "Hide sources" : "Show sources"}>
                <IconButton
                  size="small"
                  onClick={() => toggleSourceVisibility(message.id)}
                  sx={{ 
                    color: message.sender === 'user' ? 'white' : 'text.secondary',
                    '&:hover': {
                      backgroundColor: message.sender === 'user' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.04)',
                    }
                  }}
                >
                  {visibleSources.has(message.id) ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </Tooltip>
              
              {visibleSources.has(message.id) && (
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
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
            </Box>
          )}
          
          <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
            {message.timestamp.toLocaleTimeString()}
          </Typography>
        </Paper>
      </Box>
    </Box>
    );
  };

  const awsServices = [
    {
      title: 'Compute Services',
      icon: <SpeedIcon />,
      description: 'EC2, Lambda, ECS, EKS',
      color: '#ff6b35',
    },
    {
      title: 'Storage Services',
      icon: <StorageIcon />,
      description: 'S3, EBS, EFS, Glacier',
      color: '#4ecdc4',
    },
    {
      title: 'Security & Identity',
      icon: <SecurityIcon />,
      description: 'IAM, Cognito, KMS, Secrets Manager',
      color: '#45b7d1',
    },
    {
      title: 'Monitoring & Analytics',
      icon: <AnalyticsIcon />,
      description: 'CloudWatch, CloudTrail, X-Ray',
      color: '#96ceb4',
    },
  ];

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
        <CloudIcon sx={{ fontSize: 40, color: '#ff6b35', mr: 2 }} />
        <Typography variant="h5" sx={{ color: '#0000fe', fontWeight: 'bold' }}>
          ☁️ AWS IT Solutions
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
          minHeight: 0,
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
              <CloudIcon sx={{ fontSize: 80, color: '#ff6b35', mb: 3 }} />
              <Typography variant="h4" sx={{ color: '#0000fe', fontWeight: 'bold', mb: 2 }}>
                AWS Cloud Solutions Hub
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
                Get expert guidance on AWS cloud services, architecture, deployment strategies, and best practices.
              </Typography>
              
              {/* AWS Services Overview */}
              <Grid container spacing={2} sx={{ mb: 4, maxWidth: 800 }}>
                {awsServices.map((service, index) => (
                  <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card sx={{ height: '100%', textAlign: 'center', border: '1px solid #e0e0e0' }}>
                      <CardContent>
                        <Avatar sx={{ bgcolor: service.color, mx: 'auto', mb: 2, width: 56, height: 56 }}>
                          {service.icon}
                        </Avatar>
                        <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                          {service.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {service.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              
              {/* Quick suggestions */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center', maxWidth: 800 }}>
                {[
                  "What is AWS EC2?",
                  "How to set up AWS Lambda?",
                  "Explain AWS S3 storage",
                  "What is AWS CloudFormation?"
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
                        AWS Assistant is thinking...
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
          {/* Suggested Questions */}
          <Box sx={{ 
            mb: 2,
            overflowX: 'auto',
            '&::-webkit-scrollbar': {
              height: 6,
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: '#f1f1f1',
              borderRadius: 3,
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: '#c1c1c1',
              borderRadius: 3,
              '&:hover': {
                backgroundColor: '#a8a8a8',
              },
            },
          }}>
            <Box sx={{ 
              display: 'flex', 
              gap: 1.5, 
              pb: 1,
              minWidth: 'max-content',
            }}>
              {[
                'What is AWS EC2?',
                'How to set up AWS Lambda?',
                'Explain AWS S3 storage',
                'What is AWS CloudFormation?',
                'How to configure AWS VPC?',
                'Explain AWS RDS database',
                'What is AWS IAM security?',
                'How to use AWS CloudWatch?',
                'Explain AWS ECS containers',
                'What is AWS Route 53?'
              ].map((question, index) => (
                <Chip
                  key={index}
                  label={question}
                  onClick={() => setInputMessage(question)}
                  sx={{
                    backgroundColor: '#0000fe',
                    color: 'white',
                    fontWeight: 500,
                    fontSize: '0.875rem',
                    height: 32,
                    '&:hover': {
                      backgroundColor: '#0000cc',
                      cursor: 'pointer',
                    },
                    '& .MuiChip-label': {
                      px: 1.5,
                      whiteSpace: 'nowrap',
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask about AWS services, architecture, deployment..."
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
              <Accordion 
                expanded={recentSearchesExpanded}
                onChange={(event, isExpanded) => setRecentSearchesExpanded(isExpanded)}
                sx={{ boxShadow: 'none', '&:before': { display: 'none' } }}
              >
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
                      Recent AWS searches
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {searchHistory && searchHistory.length > 0 ? searchHistory.slice(0, 5).map((item) => (
                      <Box
                        key={item.id}
                        sx={{
                          border: '1px solid #e0e0e0',
                          borderRadius: 2,
                          p: 2,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            borderColor: '#0000fe',
                            backgroundColor: '#f0f0ff',
                          },
                        }}
                        onClick={() => addHistoryToChat(item)}
                      >
                        {/* Question - User message style */}
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                          <Box sx={{ 
                            width: 24, 
                            height: 24, 
                            borderRadius: '50%', 
                            backgroundColor: '#0000fe', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            mr: 1.5,
                            flexShrink: 0
                          }}>
                            <Typography sx={{ color: 'white', fontSize: '0.75rem', fontWeight: 'bold' }}>
                              U
                            </Typography>
                          </Box>
                          <Box sx={{ flex: 1 }}>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                color: '#333',
                                fontSize: '0.875rem',
                                lineHeight: 1.4,
                                fontWeight: 500
                              }}
                            >
                              {item.query || 'Unknown query'}
                            </Typography>
                          </Box>
                        </Box>
                        
                        {/* Answer - Bot message style */}
                        {item.answer && (
                          <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                            <Box sx={{ 
                              width: 24, 
                              height: 24, 
                              borderRadius: '50%', 
                              backgroundColor: '#f0f0f0', 
                              display: 'flex', 
                              alignItems: 'center', 
                              justifyContent: 'center',
                              mr: 1.5,
                              flexShrink: 0
                            }}>
                              <Typography sx={{ color: '#666', fontSize: '0.75rem', fontWeight: 'bold' }}>
                                🤖
                              </Typography>
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Box sx={{ 
                                display: '-webkit-box',
                                WebkitLineClamp: 3,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}>
                                <FormattedText 
                                  text={item.answer.length > 150 ? `${item.answer.substring(0, 150)}...` : item.answer}
                                  variant="body2"
                                  color="#666"
                                />
                              </Box>
                            </Box>
                          </Box>
                        )}
                        
                        {/* Response time and timestamp */}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5, pt: 1, borderTop: '1px solid #f0f0f0' }}>
                          {item.response_time_ms && (
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                color: '#999',
                                fontSize: '0.7rem'
                              }}
                            >
                              {item.response_time_ms}ms
                            </Typography>
                          )}
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              color: '#999',
                              fontSize: '0.7rem'
                            }}
                          >
                            {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                          </Typography>
                        </Box>
                      </Box>
                    )) : (
                      <Typography variant="body2" color="text.secondary">
                        No recent AWS searches
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

export default AwsSolutions;