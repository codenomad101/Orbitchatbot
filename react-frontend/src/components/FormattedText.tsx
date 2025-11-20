import React from 'react';
import { marked } from 'marked';
import {
  Typography,
  Box,
} from '@mui/material';

interface FormattedTextProps {
  text: string;
  variant?: 'body1' | 'body2' | 'caption';
  color?: string;
}

// Configure marked options once outside the component
marked.setOptions({
  breaks: true,
  gfm: true,
});

const FormattedText: React.FC<FormattedTextProps> = ({ 
  text, 
  variant = 'body1', 
  color = 'inherit' 
}) => {
  const formatText = (text: string) => {
    if (!text) return null;

    // Debug: Check if text is actually a string
    if (typeof text !== 'string') {
      console.error('FormattedText received non-string:', typeof text, text);
      return (
        <Typography
          variant={variant}
          sx={{
            color: color,
            mb: 2,
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
          }}
        >
          Error: Expected string but received {typeof text}
        </Typography>
      );
    }

    try {
      // Convert markdown to HTML (options already configured)
      const htmlContent = marked.parse(text);
      
      // Ensure htmlContent is a string
      const htmlString = typeof htmlContent === 'string' ? htmlContent : String(htmlContent);

      return (
        <Box
          sx={{
            '& h1, & h2, & h3, & h4, & h5, & h6': {
              fontWeight: 'bold',
              color: color,
              marginBottom: 2,
              marginTop: 3,
              lineHeight: 1.4,
            },
            '& p': {
              marginBottom: 2,
              lineHeight: 1.6,
              color: color,
            },
            '& ul, & ol': {
              marginBottom: 2,
              paddingLeft: 3,
              color: color,
              '& li': {
                marginBottom: 1,
                lineHeight: 1.6,
              },
            },
            '& pre, & code': {
              backgroundColor: '#f5f5f5',
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              padding: 2,
              margin: '16px 0',
              overflowX: 'auto',
              fontFamily: 'Monaco, Consolas, "Courier New", monospace',
              fontSize: '0.9em',
              lineHeight: 1.4,
              color: '#333',
              whiteSpace: 'pre-wrap',
            },
            '& blockquote': {
              borderLeft: '4px solid #0000fe',
              margin: '16px 0',
              paddingLeft: 2,
              color: color,
              fontStyle: 'italic',
            },
            '& strong': {
              fontWeight: 'bold',
              color: color,
            },
            '& em': {
              fontStyle: 'italic',
              color: color,
            },
            '& a': {
              color: '#0000fe',
              textDecoration: 'underline',
              '&:hover': {
                textDecoration: 'none',
              },
            },
            '& hr': {
              border: 'none',
              borderTop: '1px solid #e0e0e0',
              margin: '24px 0',
            },
          }}
          dangerouslySetInnerHTML={{ __html: htmlString }}
        />
      );
    } catch (error) {
      console.error('Error parsing markdown:', error);
      // Fallback to plain text if markdown parsing fails
      return (
        <Typography
          variant={variant}
          sx={{
            color: color,
            mb: 2,
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
          }}
        >
          {text}
        </Typography>
      );
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {formatText(text)}
    </Box>
  );
};

export default FormattedText;