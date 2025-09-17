import ollama
from typing import Dict, List, Any, Optional
from services.simple_intent_classifier import SimpleIntentClassifier, IntentType
from services.response_formatter import ResponseFormatter
from utils import config
import logging

logger = logging.getLogger(__name__)

class ModelRouter:
    def __init__(self):
        self.client = ollama.Client(host=config.config.OLLAMA_HOST)
        self.intent_classifier = SimpleIntentClassifier()
        self.response_formatter = ResponseFormatter()
        
        # Model configurations - All limited to 500 characters max
        self.models = {
            IntentType.GENERAL: {
                'model': 'llama3.2:1b',
                'temperature': 0.7,
                'top_p': 0.9,
                'max_tokens': 400  # Balanced general responses
            },
            IntentType.CODE: {
                'model': 'codegemma:2b',  # Using CodeGemma 2B
                'temperature': 0.1,
                'top_p': 0.95,
                'max_tokens': 600  # Longer code responses for complete examples
            },
            IntentType.TECHNICAL: {
                'model': 'llama3.2:1b',
                'temperature': 0.7,  # Higher temperature for more creative/helpful responses
                'top_p': 0.9,
                'max_tokens': 500  # Balanced technical responses
            },
            IntentType.DOCUMENT_QUERY: {
                'model': 'llama3.2:1b',
                'temperature': 0.6,  # Higher temperature for more helpful responses
                'top_p': 0.9,
                'max_tokens': 500  # Balanced document answers
            },
            IntentType.SUMMARIZE: {
                'model': 'llama3.2:1b',
                'temperature': 0.3,  # Lower temperature for focused summaries
                'top_p': 0.9,
                'max_tokens': 300  # Concise summaries
            },
            IntentType.UNKNOWN: {
                'model': 'llama3.2:1b',
                'temperature': 0.5,
                'top_p': 0.9,
                'max_tokens': 400  # Balanced unknown responses
            }
        }
        
        # Check available models
        self._check_available_models()
    
    def _check_available_models(self):
        """Check which models are available and update configurations"""
        try:
            available_models = self.client.list()
            model_names = [model['name'] for model in available_models.get('models', [])]
            
            logger.info(f"Available models: {model_names}")
            
            # Update model configurations based on availability
            for intent_type, config in self.models.items():
                if config['model'] not in model_names:
                    logger.warning(f"Model {config['model']} not available, falling back to llama3.2:1b")
                    config['model'] = 'llama3.2:1b'
            
        except Exception as e:
            logger.error(f"Error checking available models: {e}")
            # Fallback to default model for all intents
            for config in self.models.values():
                config['model'] = 'llama3.2:1b'
    
    def route_query(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """
        Route a query to the appropriate model based on intent classification
        
        Returns:
            Dict containing response, intent, model used, and metadata
        """
        try:
            # Classify intent
            intent, confidence, metadata = self.intent_classifier.classify_intent(query)
            
            # Get model configuration
            model_config = self.models.get(intent, self.models[IntentType.UNKNOWN])
            
            # Generate response using appropriate model
            response = self._generate_response(
                query=query,
                context=context,
                model_config=model_config,
                intent=intent
            )
            
            # Format the response
            formatted_response = self.response_formatter.format_response(response, intent.value)
            
            return {
                'response': formatted_response,
                'intent': intent.value,
                'confidence': confidence,
                'model_used': model_config['model'],
                'metadata': metadata,
                'explanation': self.intent_classifier.get_intent_explanation(intent, confidence, metadata)
            }
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            # Fallback to default model
            return self._fallback_response(query, context, str(e))
    
    def _generate_response(self, query: str, context: List[str], model_config: Dict, intent: IntentType) -> str:
        """Generate response using the specified model configuration"""
        try:
            # Prepare the prompt based on intent
            prompt = self._prepare_prompt(query, context, intent)
            
            # Generate response using Ollama
            response = self.client.chat(
                model=model_config['model'],
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': model_config['temperature'],
                    'top_p': model_config['top_p'],
                    'num_predict': model_config['max_tokens']
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating response with {model_config['model']}: {e}")
            raise
    
    def _prepare_prompt(self, query: str, context: List[str], intent: IntentType) -> str:
        """Prepare the prompt based on intent type"""
        if context:
            context_text = "\n\n".join(context)
            
            if intent == IntentType.CODE:
                return f"""Write clean, complete code. Provide a well-commented solution with examples if helpful.

Context:
{context_text}

Question: {query}

Provide a complete code solution:"""
            
            elif intent == IntentType.TECHNICAL:
                return f"""You are a technical expert. Answer the question concisely based on the provided context. Focus on the most relevant information. Be precise and to the point.

Context:
{context_text}

Question: {query}

Provide a focused technical explanation:"""
            
            elif intent == IntentType.DOCUMENT_QUERY:
                return f"""You are a helpful assistant. Answer the question concisely based on the provided documents. Focus on the most relevant information from the documents. Be precise and to the point.

Context:
{context_text}

Question: {query}

Provide a focused explanation based on the documents:"""
            
            elif intent == IntentType.SUMMARIZE:
                return f"""You are a summarization expert. Create a concise, well-structured summary of the provided content. Focus on the key points and main ideas. Use bullet points (•) for clarity.

Context:
{context_text}

Question: {query}

Provide a clear, concise summary:"""
            
            else:  # GENERAL or UNKNOWN
                return f"""Provide a helpful and comprehensive answer. Be informative and detailed.

Context:
{context_text}

Question: {query}

Provide a detailed response:"""
        else:
            # No context provided
            if intent == IntentType.CODE:
                return f"""Write clean, complete code. Provide a well-commented solution with examples if helpful.

{query}

Provide a complete code solution:"""
            
            elif intent == IntentType.TECHNICAL:
                return f"""You are a technical expert. Answer the question concisely with your best technical knowledge. Be precise and to the point. Use bullet points (•) for key points.

{query}

Provide a focused technical explanation:"""
            
            elif intent == IntentType.SUMMARIZE:
                return f"""You are a summarization expert. Create a concise, well-structured summary of the provided content. Focus on the key points and main ideas. Use bullet points (•) for clarity.

{query}

Provide a clear, concise summary:"""
            
            else:
                return query
    
    def _fallback_response(self, query: str, context: List[str], error: str) -> Dict[str, Any]:
        """Fallback response when routing fails"""
        try:
            # Use default model for fallback
            response = self.client.chat(
                model='llama3.2:1b',
                messages=[
                    {
                        'role': 'user',
                        'content': query
                    }
                ]
            )
            
            return {
                'response': response['message']['content'],
                'intent': 'fallback',
                'confidence': 0.0,
                'model_used': 'llama3.2:1b',
                'metadata': {'error': error},
                'explanation': 'Fallback response due to routing error'
            }
            
        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'intent': 'error',
                'confidence': 0.0,
                'model_used': 'none',
                'metadata': {'error': str(e)},
                'explanation': 'Error response'
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            available_models = self.client.list()
            return [model['name'] for model in available_models.get('models', [])]
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def test_model_connection(self, model_name: str) -> bool:
        """Test connection to a specific model"""
        try:
            response = self.client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
            return True
        except Exception as e:
            logger.error(f"Error testing model {model_name}: {e}")
            return False
