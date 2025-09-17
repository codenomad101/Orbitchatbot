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
    SUMMARIZE = "summarize"
    UNKNOWN = "unknown"

class SimpleIntentClassifier:
    def __init__(self):
        # Code-related patterns (high priority)
        self.code_patterns = [
            r'\bwrite\s+a\s+\w+\s+function\b',
            r'\bcreate\s+a\s+\w+\s+function\b',
            r'\bimplement\s+a\s+\w+\b',
            r'\bdef\s+\w+\s*\(',
            r'\bfunction\s+\w+\s*\(',
            r'\bclass\s+\w+',
            r'\bimport\s+\w+',
            r'\bfrom\s+\w+\s+import',
            r'\bSELECT\s+.*\s+FROM',
            r'\bINSERT\s+INTO',
            r'\bUPDATE\s+.*\s+SET',
            r'\bDELETE\s+FROM',
            r'<html>', r'<div>', r'<script>',
            r'\.py$', r'\.js$', r'\.java$', r'\.cpp$', r'\.sql$',
            r'\breverse\s+a\s+string\b',
            r'\bto\s+reverse\s+a\s+string\b',
            r'\bhow\s+to\s+reverse\b',
            r'\bstring.*reverse\b',
            r'\breverse.*string\b',
            r'\bpython.*reverse\b',
            r'\breverse.*python\b'
        ]
        
        # Code keywords
        self.code_keywords = [
            'function', 'class', 'method', 'variable', 'import', 'def', 'return',
            'python', 'javascript', 'java', 'c++', 'sql', 'html', 'css', 'react',
            'api', 'database', 'algorithm', 'debug', 'error', 'exception',
            'syntax', 'compile', 'execute', 'run', 'test', 'unit test',
            'framework', 'library', 'package', 'module', 'dependency',
            'git', 'github', 'repository', 'commit', 'branch', 'merge',
            'docker', 'kubernetes', 'deployment', 'server', 'client',
            'frontend', 'backend', 'fullstack', 'devops', 'ci/cd',
            'reverse', 'string', 'sort', 'search', 'find', 'replace'
        ]
        
        # Technical keywords
        self.technical_keywords = [
            'architecture', 'design pattern', 'system', 'infrastructure',
            'performance', 'optimization', 'scalability', 'security',
            'database design', 'data structure', 'algorithm', 'complexity',
            'machine learning', 'ai', 'neural network', 'deep learning',
            'cloud', 'aws', 'azure', 'gcp', 'microservices', 'api design',
            'explain', 'describe', 'what is', 'how does', 'concept', 'theory',
            'difference', 'compare', 'versus', 'vs', 'between', 'different',
            'version', 'v1', 'v2', 'v3', 'model', 'type', 'specification',
            'technical', 'technology', 'component', 'feature', 'capability',
            'monitoring', 'lubrication', 'system', 'device', 'equipment'
        ]
        
        # Summarization keywords
        self.summarize_keywords = [
            'summarize', 'summary', 'summarise', 'brief', 'overview',
            'key points', 'main points', 'highlights', 'recap', 'recapitulate',
            'condense', 'abbreviate', 'shorten', 'compress', 'digest',
            'tl;dr', 'tldr', 'in short', 'in brief', 'to summarize'
        ]
        
        # Document query indicators
        self.document_keywords = [
            'document', 'file', 'pdf', 'text', 'content', 'information',
            'search', 'find', 'lookup', 'reference', 'manual', 'guide',
            'tutorial', 'explanation', 'definition', 'meaning'
        ]
    
    def classify_intent(self, query: str) -> Tuple[IntentType, float, Dict[str, any]]:
        """Classify the intent of a user query"""
        query_lower = query.lower().strip()
        
        # Check for code patterns first (highest priority)
        code_score = self._calculate_code_score(query_lower)
        if code_score > 0.3:  # Lower threshold
            return IntentType.CODE, code_score, {
                'reason': 'Code patterns or keywords detected',
                'patterns_found': self._find_code_patterns(query),
                'keywords_found': self._find_code_keywords(query_lower)
            }
        
        # Check for summarization keywords
        summarize_score = self._calculate_summarize_score(query_lower)
        if summarize_score > 0.3:  # High threshold for summarization
            return IntentType.SUMMARIZE, summarize_score, {
                'reason': 'Summarization keywords detected',
                'keywords_found': self._find_summarize_keywords(query_lower)
            }
        
        # Check for technical keywords
        technical_score = self._calculate_technical_score(query_lower)
        if technical_score > 0.2:  # Lower threshold
            return IntentType.TECHNICAL, technical_score, {
                'reason': 'Technical keywords detected',
                'keywords_found': self._find_technical_keywords(query_lower)
            }
        
        # Check for document query indicators
        document_score = self._calculate_document_score(query_lower)
        if document_score > 0.2:  # Lower threshold
            return IntentType.DOCUMENT_QUERY, document_score, {
                'reason': 'Document query indicators detected',
                'keywords_found': self._find_document_keywords(query_lower)
            }
        
        # Check for general conversation
        general_score = self._calculate_general_score(query_lower)
        if general_score > 0.1:  # Lower threshold
            return IntentType.GENERAL, general_score, {
                'reason': 'General conversation detected',
                'indicators': self._find_general_indicators(query_lower)
            }
        
        # Default to general if no clear intent
        return IntentType.GENERAL, 0.5, {
            'reason': 'Default to general conversation',
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
        
        # Check for code patterns (highest priority)
        pattern_matches = sum(1 for pattern in self.code_patterns if re.search(pattern, query, re.IGNORECASE))
        if pattern_matches > 0:
            score += 0.8  # High weight for patterns
        
        # Check for specific code-related phrases (high priority)
        code_phrases = ['write a', 'create a', 'implement', 'function', 'class', 'method']
        phrase_matches = sum(1 for phrase in code_phrases if phrase in query)
        if phrase_matches > 0:
            score += 0.6
        
        # Check for code keywords (lower priority, but exclude ambiguous ones)
        ambiguous_keywords = ['algorithm', 'api', 'database', 'server', 'client']
        code_keywords_filtered = [kw for kw in self.code_keywords if kw not in ambiguous_keywords]
        keyword_matches = sum(1 for keyword in code_keywords_filtered if keyword in query)
        if keyword_matches > 0:
            score += min(keyword_matches / 3.0, 1.0) * 0.4
        
        return min(score, 1.0)
    
    def _calculate_technical_score(self, query: str) -> float:
        """Calculate score for technical intent"""
        keyword_matches = sum(1 for keyword in self.technical_keywords if keyword in query)
        if keyword_matches > 0:
            return min(keyword_matches / 2.0, 1.0) * 0.8
        return 0.0
    
    def _calculate_document_score(self, query: str) -> float:
        """Calculate score for document query intent"""
        keyword_matches = sum(1 for keyword in self.document_keywords if keyword in query)
        if keyword_matches > 0:
            return min(keyword_matches / 2.0, 1.0) * 0.7
        return 0.0
    
    def _calculate_summarize_score(self, query: str) -> float:
        """Calculate score for summarization intent"""
        score = 0.0
        
        # Check for summarization keywords
        for keyword in self.summarize_keywords:
            if keyword in query:
                score += 0.3  # High weight for summarization keywords
        
        # Check for summarization patterns
        summarize_patterns = [
            r'\bsummarize\b', r'\bsummary\b', r'\bbrief\b', r'\boverview\b',
            r'\bkey points\b', r'\bmain points\b', r'\bhighlights\b',
            r'\btl;dr\b', r'\btldr\b', r'\bin short\b', r'\bin brief\b'
        ]
        
        for pattern in summarize_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.4  # Very high weight for patterns
        
        return min(score, 1.0)
    
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
            return 0.6
        
        # Check for conversational patterns
        conversational_patterns = [
            r'\bhow are you\b', r'\bwhat\'s up\b', r'\btell me about\b',
            r'\bcan you help\b', r'\bwhat do you think\b'
        ]
        
        pattern_matches = sum(1 for pattern in conversational_patterns if re.search(pattern, query, re.IGNORECASE))
        if pattern_matches > 0:
            return 0.6
        
        return 0.3  # Default general score
    
    def _find_code_patterns(self, query: str) -> List[str]:
        """Find code patterns in the query"""
        found_patterns = []
        for pattern in self.code_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                found_patterns.append(pattern)
        return found_patterns
    
    def _find_code_keywords(self, query: str) -> List[str]:
        """Find code keywords in the query"""
        return [keyword for keyword in self.code_keywords if keyword in query]
    
    def _find_technical_keywords(self, query: str) -> List[str]:
        """Find technical keywords in the query"""
        return [keyword for keyword in self.technical_keywords if keyword in query]
    
    def _find_document_keywords(self, query: str) -> List[str]:
        """Find document keywords in the query"""
        return [keyword for keyword in self.document_keywords if keyword in query]
    
    def _find_summarize_keywords(self, query: str) -> List[str]:
        """Find summarization keywords in the query"""
        return [keyword for keyword in self.summarize_keywords if keyword in query]
    
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
