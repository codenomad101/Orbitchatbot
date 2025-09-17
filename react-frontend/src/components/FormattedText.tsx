import React from 'react';
import {
  Typography,
  Box,
  Paper,
} from '@mui/material';

interface FormattedTextProps {
  text: string;
  variant?: 'body1' | 'body2' | 'caption';
  color?: string;
}

const FormattedText: React.FC<FormattedTextProps> = ({ 
  text, 
  variant = 'body1', 
  color = 'inherit' 
}) => {
  const formatText = (text: string) => {
    if (!text) return null;

    const lines = text.split('\n');
    const formatted = [];
    let currentList = [];
    let listType = null;

    const flushList = () => {
      if (currentList.length > 0) {
        if (listType === 'numbered') {
          formatted.push(
            <Box key={`numbered-list-${formatted.length}`} sx={{ mb: 2 }}>
              {currentList.map((item, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    mb: 1,
                  }}
                >
                  <Typography
                    sx={{
                      color: color,
                      mr: 1.5,
                      fontWeight: 'bold',
                      minWidth: '24px',
                      lineHeight: 1.6,
                    }}
                  >
                    {item.number}.
                  </Typography>
                  <Typography
                    variant={variant}
                    sx={{
                      color: color,
                      flex: 1,
                      lineHeight: 1.6,
                    }}
                  >
                    {item.content}
                  </Typography>
                </Box>
              ))}
            </Box>
          );
        } else if (listType === 'bullet') {
          formatted.push(
            <Box key={`bullet-list-${formatted.length}`} sx={{ mb: 2 }}>
              {currentList.map((item, idx) => (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    mb: 1,
                  }}
                >
                  <Typography
                    sx={{
                      color: color,
                      mr: 1.5,
                      fontSize: '1.2em',
                      lineHeight: 1.6,
                      minWidth: '16px',
                    }}
                  >
                    •
                  </Typography>
                  <Typography
                    variant={variant}
                    sx={{
                      color: color,
                      flex: 1,
                      lineHeight: 1.6,
                    }}
                  >
                    {item}
                  </Typography>
                </Box>
              ))}
            </Box>
          );
        }
        currentList = [];
        listType = null;
      }
    };

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // Skip empty lines but add spacing between sections
      if (trimmedLine === '') {
        flushList();
        return;
      }

      // Handle headers (text wrapped in **)
      if (trimmedLine.match(/^\*\*.*\*\*$/)) {
        flushList();
        const headerText = trimmedLine.replace(/\*\*/g, '');
        formatted.push(
          <Typography
            key={`header-${index}`}
            variant="h6"
            sx={{
              fontWeight: 'bold',
              color: color,
              mb: 2,
              mt: formatted.length > 0 ? 3 : 0,
            }}
          >
            {headerText}
          </Typography>
        );
        return;
      }

      // Handle numbered lists
      const numberMatch = trimmedLine.match(/^(\d+)\.\s*(.*)/);
      if (numberMatch) {
        const [, number, content] = numberMatch;
        if (listType !== 'numbered') {
          flushList();
          listType = 'numbered';
        }
        currentList.push({
          number: parseInt(number),
          content: content
        });
        return;
      }

      // Handle bullet points (lines starting with •)
      if (trimmedLine.startsWith('•')) {
        if (listType !== 'bullet') {
          flushList();
          listType = 'bullet';
        }
        const bulletText = trimmedLine.substring(1).trim();
        currentList.push(bulletText);
        return;
      }

      // Handle code blocks (lines starting with spaces or containing code patterns)
      if (line.startsWith('    ') || 
          trimmedLine.includes('def ') || 
          trimmedLine.includes('function ') ||
          trimmedLine.includes('const ') ||
          trimmedLine.includes('import ') ||
          /^[a-zA-Z_$][a-zA-Z0-9_$]*\s*[=:({]/.test(trimmedLine)) {
        flushList();
        formatted.push(
          <Paper
            key={`code-${index}`}
            elevation={0}
            sx={{
              p: 2,
              backgroundColor: '#f5f5f5',
              border: '1px solid #e0e0e0',
              borderRadius: 1,
              mb: 2,
              overflow: 'auto',
            }}
          >
            <Typography
              component="pre"
              sx={{
                color: '#333',
                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                fontSize: '0.9em',
                lineHeight: 1.4,
                whiteSpace: 'pre-wrap',
                margin: 0,
              }}
            >
              {line}
            </Typography>
          </Paper>
        );
        return;
      }

      // Handle regular paragraphs
      if (trimmedLine) {
        flushList();
        formatted.push(
          <Typography
            key={`para-${index}`}
            variant={variant}
            sx={{
              color: color,
              mb: 2,
              lineHeight: 1.6,
            }}
          >
            {trimmedLine}
          </Typography>
        );
      }
    });

    // Flush any remaining list
    flushList();

    return formatted;
  };

  return (
    <Box sx={{ width: '100%' }}>
      {formatText(text)}
    </Box>
  );
};

export default FormattedText;