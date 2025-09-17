import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import FormattingDemo from '../components/FormattingDemo';

const FormattingTest: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 4, color: '#0000fe', textAlign: 'center' }}>
        🎨 Frontend Text Formatting Test
      </Typography>
      
      <FormattingDemo />
      
      <Box sx={{ mt: 4, p: 2, backgroundColor: '#f0f8ff', borderRadius: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, color: '#0000fe' }}>
          📋 Formatting Features Implemented:
        </Typography>
        <Typography variant="body1" component="div">
          • <strong>Headers:</strong> Text wrapped in ** becomes bold headers<br/>
          • <strong>Bullet Points:</strong> Lines starting with • become proper bullet lists<br/>
          • <strong>Numbered Lists:</strong> Lines starting with numbers become numbered lists<br/>
          • <strong>Code Blocks:</strong> Indented text or code patterns get code formatting<br/>
          • <strong>Paragraph Spacing:</strong> Proper spacing between sections<br/>
          • <strong>Color Support:</strong> Maintains theme colors for user/bot messages
        </Typography>
      </Box>
    </Container>
  );
};

export default FormattingTest;
