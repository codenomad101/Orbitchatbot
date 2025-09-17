import React, { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material';
import FormattedText from './FormattedText';

interface ExpandableTextProps {
  text: string;
  variant?: 'body1' | 'body2' | 'caption';
  color?: string;
  previewLength?: number;
}

const ExpandableText: React.FC<ExpandableTextProps> = ({ 
  text, 
  variant = 'body1', 
  color = 'inherit',
  previewLength = 1200 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Check if text is long enough to need expansion
  const needsExpansion = text.length > previewLength;
  
  // Get preview text (first 800 characters, breaking at word boundary)
  const getPreviewText = (text: string, length: number) => {
    if (text.length <= length) return text;
    
    const preview = text.substring(0, length);
    const lastSpaceIndex = preview.lastIndexOf(' ');
    
    // If we can break at a word boundary, do so
    if (lastSpaceIndex > length * 0.8) {
      return preview.substring(0, lastSpaceIndex) + '...';
    }
    
    return preview + '...';
  };
  
  const displayText = isExpanded || !needsExpansion ? text : getPreviewText(text, previewLength);
  
  return (
    <Box>
      <FormattedText 
        text={displayText} 
        variant={variant} 
        color={color} 
      />
      
      {needsExpansion && (
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-start' }}>
          <Button
            size="small"
            onClick={() => setIsExpanded(!isExpanded)}
            startIcon={isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{
              color: color,
              textTransform: 'none',
              fontSize: '0.875rem',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
              }
            }}
          >
            {isExpanded ? 'Show Less' : 'Read More'}
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ExpandableText;
