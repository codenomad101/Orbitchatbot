import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import SkfLogo from '../assets/Skf_logo_white.svg';
import {
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  Folder as DocumentsIcon,
  People as PeopleIcon,
  Analytics as AnalyticsIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 280;
const collapsedDrawerWidth = 64;

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
    navigate('/login');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Chat', icon: <ChatIcon />, path: '/dashboard' },
    ...(isAdmin ? [
      { text: 'Documents', icon: <DocumentsIcon />, path: '/documents' },
      { text: 'Users', icon: <PeopleIcon />, path: '/users' },
      { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
    ] : []),
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ 
        backgroundColor: '#0000fe', 
        borderBottom: '1px solid #0000cc', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        minHeight: '64px'
      }}>
        {!sidebarCollapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <img 
              src={SkfLogo} 
              alt="SKF Logo" 
              style={{ 
                height: '32px', 
                width: 'auto',
                filter: 'brightness(0) invert(1)' // Make logo white for blue background
              }} 
            />
            <Typography variant="h6" component="div" sx={{ 
              color: 'white', 
              fontWeight:'bold',
              fontSize: '20px'
            }}>
              Orbitbot
            </Typography>
          </Box>
        )}
        {sidebarCollapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
            {/* Logo hidden when sidebar is collapsed */}
          </Box>
        )}
        <IconButton 
          onClick={handleSidebarToggle} 
          sx={{ 
            color: 'white',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            },
            '& .MuiSvgIcon-root': {
              color: 'white',
            }
          }}
        >
          {sidebarCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Toolbar>
      <Divider />
      <List sx={{ flexGrow: 1, pt: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
              sx={{
                borderRadius: 1,
                mx: 1,
                justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                '&.Mui-selected': {
                  backgroundColor: '#0000fe',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: '#0000cc',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  backgroundColor: '#f0f0ff',
                },
              }}
              title={sidebarCollapsed ? item.text : undefined}
            >
              <ListItemIcon sx={{ minWidth: sidebarCollapsed ? 'auto' : 40, justifyContent: 'center' }}>
                {item.icon}
              </ListItemIcon>
              {!sidebarCollapsed && <ListItemText primary={item.text} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${sidebarCollapsed ? collapsedDrawerWidth : drawerWidth}px)` },
          ml: { sm: `${sidebarCollapsed ? collapsedDrawerWidth : drawerWidth}px` },
          backgroundColor: '#0000fe',
          color: 'white',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          transition: 'width 0.3s ease, margin-left 0.3s ease',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2, 
              display: { sm: 'none' },
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              '& .MuiSvgIcon-root': {
                color: 'white',
              }
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, color: 'white' }}>
            Your Personal Orbit Assistant
          </Typography>
          
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="profile-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <Avatar sx={{ bgcolor: '#0000fe' }}>
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
          
          <Menu
            id="profile-menu"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
          >
            <MenuItem disabled>
              <Typography variant="body2" color="text.secondary">
                {user?.username} ({user?.role})
              </Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: sidebarCollapsed ? collapsedDrawerWidth : drawerWidth }, flexShrink: { sm: 0 }, transition: 'width 0.3s ease' }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: sidebarCollapsed ? collapsedDrawerWidth : drawerWidth,
              transition: 'width 0.3s ease',
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${sidebarCollapsed ? collapsedDrawerWidth : drawerWidth}px)` },
          mt: '64px',
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: location.pathname === '/dashboard' ? '#ffffff' : '#f5f5f5',
          p: location.pathname === '/dashboard' ? 0 : 3,
          transition: 'width 0.3s ease',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;

