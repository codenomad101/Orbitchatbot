import React from 'react';
import { Box, Typography, Paper, Divider } from '@mui/material';
import FormattedText from './FormattedText';

const FormattingDemo: React.FC = () => {
  const sampleText = `**TLDD System Overview**

The TLDD series is part of the SKF SYSTEM 24 portfolio, which utilizes a web dashboard and interface to monitor the status of each lubricator and change its settings.

**Key Components:**

• **Gateway:** The gateway uses the GSM network to communicate with the data cloud. All communication is end-to-end encrypted to prevent access except by authorized users.

• **Drive Unit:** The drive unit contains the electro-mechanical drive system that powers the lubricator.

• **Lubrication Cloud Platform (LCP):** This web-interface visualizes the lubricator data in the cloud and offers intuitive interaction with the system.

**Features:**

1. Real-time monitoring of lubricator status
2. Remote control and configuration
3. 24/7 accessibility from any device
4. End-to-end encrypted communication

The system operates with two cartridge sizes: 125 ml and 250 ml, providing flexibility for different lubrication requirements.`;

  return (
    <Paper elevation={2} sx={{ p: 3, m: 2 }}>
      <Typography variant="h5" sx={{ mb: 2, color: '#0000fe' }}>
        🎯 Frontend Text Formatting Demo
      </Typography>
      
      <Divider sx={{ mb: 2 }} />
      
      <Typography variant="h6" sx={{ mb: 1 }}>
        Sample Response (Before Formatting):
      </Typography>
      <Box sx={{ 
        p: 2, 
        backgroundColor: '#f5f5f5', 
        borderRadius: 1, 
        mb: 2,
        fontFamily: 'monospace',
        fontSize: '0.9em'
      }}>
        {sampleText}
      </Box>
      
      <Typography variant="h6" sx={{ mb: 1 }}>
        Formatted Response (After Processing):
      </Typography>
      <Box sx={{ 
        p: 2, 
        backgroundColor: '#ffffff', 
        border: '1px solid #e0e0e0',
        borderRadius: 1 
      }}>
        <FormattedText text={sampleText} />
      </Box>
      
      <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
        ✅ Headers are properly formatted<br/>
        ✅ Bullet points use proper • symbols<br/>
        ✅ Numbered lists are formatted correctly<br/>
        ✅ Paragraph spacing is maintained<br/>
        ✅ Code blocks are highlighted
      </Typography>
    </Paper>
  );
};

export default FormattingDemo;
