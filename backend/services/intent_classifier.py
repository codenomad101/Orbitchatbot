import re
from typing import Dict, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class IntentType(Enum):
    GENERAL = "general"
    CODE = "code"
    DOCUMENT_QUERY = "document_query"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"

class IntentClassifier:
    def __init__(self):
        # Code-related keywords and patterns
        self.code_keywords = [
            'function', 'class', 'method', 'variable', 'import', 'def', 'return',
            'python', 'javascript', 'java', 'c++', 'sql', 'html', 'css', 'react',
            'api', 'database', 'algorithm', 'debug', 'error', 'exception',
            'syntax', 'compile', 'execute', 'run', 'test', 'unit test',
            'framework', 'library', 'package', 'module', 'dependency',
            'git', 'github', 'repository', 'commit', 'branch', 'merge',
            'docker', 'kubernetes', 'deployment', 'server', 'client',
            'frontend', 'backend', 'fullstack', 'devops', 'ci/cd'
        ]
        
        # Technical keywords (but not necessarily code)
        self.technical_keywords = [
            'architecture', 'design pattern', 'system', 'infrastructure',
            'performance', 'optimization', 'scalability', 'security',
            'database design', 'data structure', 'algorithm', 'complexity',
            'machine learning', 'ai', 'neural network', 'deep learning',
            'cloud', 'aws', 'azure', 'gcp', 'microservices', 'api design'
        ]
        
        # Document query indicators
        self.document_keywords = [
            'document', 'file', 'pdf', 'text', 'content', 'information',
            'search', 'find', 'lookup', 'reference', 'manual', 'guide',
            'tutorial', 'explanation', 'definition', 'meaning', 'what is',
            'how to', 'where is', 'when', 'why', 'who', 'which'
        ]
        
        # Code patterns
        self.code_patterns = [
            r'\bdef\s+\w+\s*\(',  # Python function definition
            r'\bfunction\s+\w+\s*\(',  # JavaScript function
            r'\bclass\s+\w+',  # Class definition
            r'\bimport\s+\w+',  # Import statement
            r'\bfrom\s+\w+\s+import',  # Python import
            r'\bconst\s+\w+\s*=',  # JavaScript const
            r'\blet\s+\w+\s*=',  # JavaScript let
            r'\bvar\s+\w+\s*=',  # JavaScript var
            r'SELECT\s+.*\s+FROM',  # SQL query
            r'INSERT\s+INTO',  # SQL insert
            r'UPDATE\s+.*\s+SET',  # SQL update
            r'DELETE\s+FROM',  # SQL delete
            r'<html>', r'<div>', r'<span>', r'<script>',  # HTML tags
            r'\.py$', r'\.js$', r'\.java$', r'\.cpp$', r'\.sql$'  # File extensions
        ]
    
    def classify_intent(self, query: str) -> Tuple[IntentType, float, Dict[str, any]]:
        """
        Classify the intent of a user query
        
        Returns:
            Tuple of (intent_type, confidence, metadata)
        """
        query_lower = query.lower().strip()
        
        # Check for code patterns first (highest priority)
        code_score = self._calculate_code_score(query_lower)
        if code_score > 0.7:
            return IntentType.CODE, code_score, {
                'reason': 'Code patterns detected',
                'patterns_found': self._find_code_patterns(query)
            }
        
        # Check for technical keywords
        technical_score = self._calculate_technical_score(query_lower)
        if technical_score > 0.6:
            return IntentType.TECHNICAL, technical_score, {
                'reason': 'Technical keywords detected',
                'keywords_found': self._find_technical_keywords(query_lower)
            }
        
        # Check for document query indicators
        document_score = self._calculate_document_score(query_lower)
        if document_score > 0.5:
            return IntentType.DOCUMENT_QUERY, document_score, {
                'reason': 'Document query indicators detected',
                'keywords_found': self._find_document_keywords(query_lower)
            }
        
        # Check for general conversation
        general_score = self._calculate_general_score(query_lower)
        if general_score > 0.4:
            return IntentType.GENERAL, general_score, {
                'reason': 'General conversation detected',
                'indicators': self._find_general_indicators(query_lower)
            }
        
        # Default to unknown
        return IntentType.UNKNOWN, 0.0, {
            'reason': 'No clear intent detected',
            'scores': {
                'code': code_score,
                'technical': technical_score,
                'document': document_score,
                'general': general_score
            }
        }
    
    def _calculate_code_score(self, query: str) -> float:
        """Calculate score for code-related intent"""
        score = 0.0
        
        # Check for code keywords
        keyword_matches = sum(1 for keyword in self.code_keywords if keyword in query)
        if keyword_matches > 0:
            score += min(keyword_matches / 5.0, 1.0) * 0.6  # More lenient scoring
        
        # Check for code patterns
        pattern_matches = sum(1 for pattern in self.code_patterns if re.search(pattern, query, re.IGNORECASE))
        if pattern_matches > 0:
            score += min(pattern_matches / 3.0, 1.0) * 0.8  # Higher weight for patterns
        
        # Check for specific code-related phrases
        code_phrases = ['write a', 'create a', 'implement', 'function', 'class', 'method', 'algorithm']
        phrase_matches = sum(1 for phrase in code_phrases if phrase in query)
        if phrase_matches > 0:
            score += min(phrase_matches / 3.0, 1.0) * 0.4
        
        return min(score, 1.0)
    
    def _calculate_technical_score(self, query: str) -> float:
        """Calculate score for technical intent"""
        keyword_matches = sum(1 for keyword in self.technical_keywords if keyword in query)
        return min((keyword_matches / len(self.technical_keywords)) * 0.8, 1.0)
    
    def _calculate_document_score(self, query: str) -> float:
        """Calculate score for document query intent"""
        keyword_matches = sum(1 for keyword in self.document_keywords if keyword in query)
        return min((keyword_matches / len(self.document_keywords)) * 0.7, 1.0)
    
    def _calculate_general_score(self, query: str) -> float:
        """Calculate score for general conversation intent"""
        # Simple heuristics for general conversation
        general_indicators = [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'please',
            'joke', 'story', 'tell me', 'explain', 'help', 'what',
            'how', 'why', 'when', 'where', 'who', 'can you'
        ]
        
        indicator_matches = sum(1 for indicator in general_indicators if indicator in query)
        if indicator_matches > 0:
            return min(indicator_matches / 3.0, 1.0) * 0.8  # More lenient scoring
        
        # Check for conversational patterns
        conversational_patterns = [
            r'\bhow are you\b', r'\bwhat\'s up\b', r'\btell me about\b',
            r'\bcan you help\b', r'\bwhat do you think\b'
        ]
        
        pattern_matches = sum(1 for pattern in conversational_patterns if re.search(pattern, query, re.IGNORECASE))
        if pattern_matches > 0:
            return 0.6
        
        return 0.0
    
    def _find_code_patterns(self, query: str) -> List[str]:
        """Find code patterns in the query"""
        found_patterns = []
        for pattern in self.code_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                found_patterns.append(pattern)
        return found_patterns
    
    def _find_technical_keywords(self, query: str) -> List[str]:
        """Find technical keywords in the query"""
        return [keyword for keyword in self.technical_keywords if keyword in query]
    
    def _find_document_keywords(self, query: str) -> List[str]:
        """Find document keywords in the query"""
        return [keyword for keyword in self.document_keywords if keyword in query]
    
    def _find_general_indicators(self, query: str) -> List[str]:
        """Find general conversation indicators in the query"""
        general_indicators = [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'please',
            'joke', 'story', 'tell me', 'explain', 'help'
        ]
        return [indicator for indicator in general_indicators if indicator in query]
    
    def get_intent_explanation(self, intent: IntentType, confidence: float, metadata: Dict) -> str:
        """Get a human-readable explanation of the intent classification"""
        explanations = {
            IntentType.CODE: f"Code-related query (confidence: {confidence:.2f}) - {metadata.get('reason', '')}",
            IntentType.TECHNICAL: f"Technical query (confidence: {confidence:.2f}) - {metadata.get('reason', '')}",
            IntentType.DOCUMENT_QUERY: f"Document search query (confidence: {confidence:.2f}) - {metadata.get('reason', '')}",
            IntentType.GENERAL: f"General conversation (confidence: {confidence:.2f}) - {metadata.get('reason', '')}",
            IntentType.UNKNOWN: f"Unclear intent (confidence: {confidence:.2f}) - {metadata.get('reason', '')}"
        }
        return explanations.get(intent, "Unknown intent")
