import re

class ResponseFormatter:
    def __init__(self, max_response_length: int = 800):  # Balanced limit for concise responses
        self.max_response_length = max_response_length
        self.code_max_length = 1200  # Longer for code responses
        self.technical_max_length = 1000  # Balanced for technical responses
        self.document_max_length = 1000  # Balanced for document responses
    
    def format_response(self, response: str, intent_type: str) -> str:
        """Format the response based on intent type"""
        if not response:
            return response
        
        # No early truncation - preserve all content
        
        # Clean up the response
        formatted = self._clean_response(response)
        
        # Apply intent-specific formatting
        if intent_type == "technical":
            formatted = self._format_technical_response(formatted)
        elif intent_type == "code":
            formatted = self._format_code_response(formatted)
        elif intent_type == "document_query":
            formatted = self._format_document_response(formatted)
        else:
            formatted = self._format_general_response(formatted)
        
        # Don't truncate responses - let frontend handle preview/expand
        # Just clean up the response without truncation
        return formatted
    
    def _clean_response(self, response: str) -> str:
        """Clean up common response issues with aggressive trimming"""
        # Remove verbose introductory phrases
        verbose_patterns = [
            r'Based on the provided context,.*?[.!?]\s*',
            r'According to the information provided,.*?[.!?]\s*',
            r'The question asks.*?[.!?]\s*',
            r'Therefore, the answer.*?[.!?]\s*',
            r'In conclusion,.*?[.!?]\s*',
            r'To summarize,.*?[.!?]\s*',
            r'Let me explain.*?[.!?]\s*',
            r'I can help you.*?[.!?]\s*',
            r'Here\'s what.*?[.!?]\s*'
        ]
        
        for pattern in verbose_patterns:
            response = re.sub(pattern, '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove repetitive content more aggressively
        sentences = self._split_sentences(response)
        unique_sentences = self._remove_duplicate_sentences(sentences)
        response = ' '.join(unique_sentences)
        
        # Remove excessive examples and explanations
        response = self._trim_examples(response)
        
        # Remove repetitive text patterns
        response = re.sub(r'(Please provide.*?\.\s*)+', '', response)
        response = re.sub(r'(Answer:.*?\.\s*)+', '', response)
        response = re.sub(r'(Note:.*?\.\s*)+', '', response)
        
        # No truncation - preserve all content
        
        # Clean up whitespace
        response = re.sub(r'\n\s*\n\s*\n+', '\n\n', response)
        response = re.sub(r' +', ' ', response)
        
        return response.strip()
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _remove_duplicate_sentences(self, sentences: list) -> list:
        """Remove duplicate or very similar sentences"""
        seen_normalized = set()
        unique_sentences = []
        
        for sentence in sentences:
            # Normalize for comparison
            normalized = re.sub(r'[^\w\s]', '', sentence.lower()).strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            
            if normalized and normalized not in seen_normalized:
                seen_normalized.add(normalized)
                unique_sentences.append(sentence)
        
        return unique_sentences
    
    def _trim_examples(self, response: str) -> str:
        """Remove excessive examples and keep only the first one"""
        # Find patterns like "For example:" or "Example:"
        example_pattern = r'(For example:|Example:).*?(?=\.|$)'
        examples = re.findall(example_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if len(examples) > 1:
            # Keep only the first example
            first_example_end = response.find(examples[1])
            if first_example_end > 0:
                response = response[:first_example_end].strip()
        
        return response
    
    def _format_technical_response(self, response: str) -> str:
        """Format technical responses with proper structure and conciseness"""
        # Clean up the response first
        response = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', response)  # Fix headers
        
        # Split into lines and process each one
        lines = response.split('\n')
        formatted_lines = []
        bullet_count = 0
        max_bullets = 5  # Limit number of bullet points
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
                
            # Handle headers
            if line.startswith('**') and line.endswith('**'):
                formatted_lines.append(line)
            # Handle bullet points - convert any bullet style to •
            elif line.startswith('•') or line.startswith('*') or line.startswith('-'):
                if bullet_count < max_bullets:
                    # Convert to proper bullet
                    line = re.sub(r'^[\*\-\•]\s*', '• ', line)
                    formatted_lines.append(line)
                    bullet_count += 1
            # Handle numbered lists
            elif re.match(r'^\d+\.', line):
                formatted_lines.append(line)
            else:
                # Regular text - preserve all content
                formatted_lines.append(line)
        
        # Join lines and clean up spacing
        result = '\n'.join(formatted_lines)
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)  # Clean up excessive spacing
        
        return result
    
    def _format_code_response(self, response: str) -> str:
        """Format code responses - keep only essential code"""
        # Extract the main function/code block
        code_match = re.search(r'def\s+\w+.*?(?=\n(?:def|\Z))', response, re.DOTALL)
        if code_match:
            return code_match.group(0).strip()
        
        # If no function found, return first code block
        code_match = re.search(r'```.*?\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        return response.strip()
    
    def _format_document_response(self, response: str) -> str:
        """Format document query responses concisely"""
        # Split into main points and keep only the most relevant
        sentences = self._split_sentences(response)
        if len(sentences) > 3:
            sentences = sentences[:3]  # Keep only first 3 sentences
        
        return '. '.join(sentences) + '.' if sentences else response
    
    def _format_general_response(self, response: str) -> str:
        """Format general responses - keep it brief"""
        sentences = self._split_sentences(response)
        if len(sentences) > 2:
            sentences = sentences[:2]  # Keep only first 2 sentences
        
        return '. '.join(sentences) + '.' if sentences else response
    
    def truncate_response(self, response: str, max_length: int = None) -> str:
        """Truncate response if too long"""
        if max_length is None:
            max_length = self.max_response_length
            
        if len(response) <= max_length:
            return response
        
        # Find a good breaking point
        truncated = response[:max_length]
        
        # Try to break at sentence boundary
        for punct in ['.', '!', '?']:
            last_punct = truncated.rfind(punct)
            if last_punct > max_length * 0.6:  # If we can break at 60% of max length
                return response[:last_punct + 1]
        
        # Try to break at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            return response[:last_space] + "..."
        
        return response[:max_length] + "..."