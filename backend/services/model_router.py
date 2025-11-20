import ollama
from typing import Dict, List, Any, Optional
from services.simple_intent_classifier import SimpleIntentClassifier, IntentType
from services.response_formatter import ResponseFormatter
from utils import config
import logging

logger = logging.getLogger(__name__)

# Try to import OpenAI and Azure OpenAI, but make it optional
try:
    from openai import OpenAI
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AZURE_OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Install with: pip install openai")

class ModelRouter:
    def __init__(self):
        # Initialize Ollama client
        self.ollama_client = ollama.Client(host=config.config.OLLAMA_HOST)
        
        # Initialize OpenAI client if available and configured
        self.openai_client = None
        if OPENAI_AVAILABLE and config.config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=config.config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Azure OpenAI client (default)
        self.azure_openai_client = None
        if AZURE_OPENAI_AVAILABLE and config.config.AZURE_OPENAI_API_KEY:
            try:
                self.azure_openai_client = AzureOpenAI(
                    api_key=config.config.AZURE_OPENAI_API_KEY,
                    azure_endpoint=config.config.AZURE_OPENAI_ENDPOINT,
                    api_version=config.config.AZURE_OPENAI_API_VERSION
                )
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI client: {e}")
        
        self.intent_classifier = SimpleIntentClassifier()
        self.response_formatter = ResponseFormatter()
        
        # Simplified model configuration - all using llama3.2:1b for speed
        self.models = {
            IntentType.GENERAL: {
                'model': 'llama3.2:1b',
                'temperature': 0.3,
                'top_p': 0.9,
                'max_tokens': 250
            },
            IntentType.CODE: {
                'model': 'llama3.2:1b',  # Using llama3.2:1b for speed
                'temperature': 0.1,
                'top_p': 0.95,
                'max_tokens': 400
            },
            IntentType.TECHNICAL: {
                'model': 'llama3.2:1b',
                'temperature': 0.4,
                'top_p': 0.9,
                'max_tokens': 300
            },
            IntentType.DOCUMENT_QUERY: {
                'model': 'llama3.2:1b',
                'temperature': 0.4,
                'top_p': 0.9,
                'max_tokens': 300
            },
            IntentType.SUMMARIZE: {
                'model': 'llama3.2:1b',
                'temperature': 0.2,
                'top_p': 0.9,
                'max_tokens': 200
            },
            IntentType.UNKNOWN: {
                'model': 'llama3.2:1b',
                'temperature': 0.3,
                'top_p': 0.9,
                'max_tokens': 250
            }
        }
        
        # Check available models
        self._check_available_models()
    
    def _check_available_models(self):
        """Check available models for both providers"""
        # Check Ollama models
        try:
            available_models = self.ollama_client.list()
            model_names = [model['name'] for model in available_models.get('models', [])]
            
            logger.info(f"Available Ollama models: {model_names}")
            
            # Since we're using llama3.2:1b for all intents, just verify it's available
            if 'llama3.2:1b' not in model_names:
                logger.error("llama3.2:1b not available! This will cause issues.")
            else:
                logger.info("llama3.2:1b is available and will be used for Ollama")
            
        except Exception as e:
            logger.error(f"Error checking Ollama models: {e}")
            logger.warning("Proceeding with llama3.2:1b configuration")
        
        # Check OpenAI availability
        if OPENAI_AVAILABLE and self.openai_client:
            logger.info(f"OpenAI is configured with model: {config.config.OPENAI_MODEL}")
        elif config.config.LLM_PROVIDER.lower() == "openai":
            logger.warning("OpenAI is set as provider but not properly configured!")
    
    def route_query(self, query: str, context: List[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Route query to appropriate LLM provider (Ollama, OpenAI, or Azure OpenAI)
        
        Args:
            query: The user's question
            context: Optional list of context strings from document search
            provider: Optional provider override ("ollama", "openai", or "azure_openai"). 
                     If None, uses config.LLM_PROVIDER
        """
        # Determine which provider to use
        if provider is None:
            provider = config.config.LLM_PROVIDER.lower()
        
        provider = provider.lower()
        
        # Route to appropriate provider
        if provider == "azure_openai" or provider == "azure":
            return self._route_azure_openai(query, context)
        elif provider == "openai":
            return self._route_openai(query, context)
        else:  # Default to Ollama
            return self._route_ollama(query, context)
    
    def _route_ollama(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """Route query to Ollama"""
        try:
            # Use model configuration optimized for speed
            model_config = {
                'model': 'llama3.2:1b',
                'temperature': 0.4,  # Balanced for speed and helpfulness
                'top_p': 0.9,
                'max_tokens': 400  # Reduced for speed
            }
            
            # Prepare fast, simple prompt
            if context:
                context_text = "\n\n".join(context[:2])  # Use first 2 context items for speed
                prompt = f"""Context: {context_text}

Question: {query}

Answer based on the context. Use **bold** for key points:"""
            else:
                prompt = f"""Question: {query}

Answer helpfully. Use **bold** for key points:"""
            
            # Direct LLM call
            response = self.ollama_client.chat(
                model=model_config['model'],
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': model_config['temperature'],
                    'top_p': model_config['top_p'],
                    'num_predict': model_config['max_tokens']
                }
            )
            
            # Simple response formatting
            formatted_response = response['message']['content'].strip()
            
            return {
                'response': formatted_response,
                'intent': 'general',  # Simplified
                'confidence': 1.0,
                'model_used': model_config['model'],
                'provider': 'ollama',
                'metadata': {},
                'explanation': 'Direct Ollama LLM call for speed'
            }
            
        except Exception as e:
            logger.error(f"Error in Ollama routing: {e}")
            return {
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'intent': 'error',
                'confidence': 0.0,
                'model_used': 'none',
                'provider': 'ollama',
                'metadata': {'error': str(e)},
                'explanation': 'Error in Ollama routing'
            }
    
    def _route_openai(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """Route query to OpenAI"""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI not available, falling back to Ollama")
                return self._route_ollama(query, context)
            
            if not self.openai_client:
                logger.warning("OpenAI client not initialized, falling back to Ollama")
                return self._route_ollama(query, context)
            
            # Prepare messages for OpenAI
            messages = []
            
            # Add context if available
            if context:
                context_text = "\n\n".join(context[:2])  # Use first 2 context items
                system_message = "You are a helpful assistant. Answer questions based on the provided context. Use **bold** for key points and format your response with proper markdown."
                user_message = f"""Context: {context_text}

Question: {query}

Answer based on the context. Use **bold** for key points:"""
            else:
                system_message = "You are a helpful assistant. Use **bold** for key points and format your response with proper markdown."
                user_message = f"""Question: {query}

Answer helpfully. Use **bold** for key points:"""
            
            messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=config.config.OPENAI_MODEL,
                messages=messages,
                temperature=config.config.OPENAI_TEMPERATURE,
                max_tokens=config.config.OPENAI_MAX_TOKENS
            )
            
            # Extract response
            formatted_response = response.choices[0].message.content.strip()
            
            return {
                'response': formatted_response,
                'intent': 'general',
                'confidence': 1.0,
                'model_used': config.config.OPENAI_MODEL,
                'provider': 'openai',
                'metadata': {
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens if response.usage else None,
                        'completion_tokens': response.usage.completion_tokens if response.usage else None,
                        'total_tokens': response.usage.total_tokens if response.usage else None
                    }
                },
                'explanation': 'OpenAI API call'
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI routing: {e}")
            # Fallback to Ollama on error
            logger.info("Falling back to Ollama due to OpenAI error")
            return self._route_ollama(query, context)
    
    def _route_azure_openai(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """Route query to Azure OpenAI (default provider)"""
        try:
            # Check if Azure OpenAI is available
            if not AZURE_OPENAI_AVAILABLE:
                logger.warning("Azure OpenAI not available, falling back to Ollama")
                return self._route_ollama(query, context)
            
            if not self.azure_openai_client:
                logger.warning("Azure OpenAI client not initialized, falling back to Ollama")
                return self._route_ollama(query, context)
            
            # Prepare messages for Azure OpenAI
            messages = []
            
            # Add context if available
            if context:
                context_text = "\n\n".join(context[:3])  # Use first 3 context items for better context
                system_message = f"""You are a helpful AI assistant. Answer questions based on the provided context.
                
Context:
{context_text}

Instructions:
- Answer based on the context provided
- If the answer is not in the context, say so clearly
- Use **bold** for key points
- Format your response with clear headings and bullet points when appropriate"""
                messages.append({"role": "system", "content": system_message})
            else:
                messages.append({
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Use **bold** for key points and format responses clearly."
                })
            
            messages.append({"role": "user", "content": query})
            
            # Call Azure OpenAI
            response = self.azure_openai_client.chat.completions.create(
                model=config.config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=config.config.AZURE_OPENAI_TEMPERATURE,
                max_tokens=config.config.AZURE_OPENAI_MAX_TOKENS
            )
            
            # Extract response
            formatted_response = response.choices[0].message.content.strip()
            
            return {
                'response': formatted_response,
                'intent': 'general',
                'confidence': 1.0,
                'model_used': config.config.AZURE_OPENAI_DEPLOYMENT_NAME,
                'provider': 'azure_openai',
                'metadata': {
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens if response.usage else None,
                        'completion_tokens': response.usage.completion_tokens if response.usage else None,
                        'total_tokens': response.usage.total_tokens if response.usage else None
                    }
                },
                'explanation': 'Azure OpenAI API call'
            }
            
        except Exception as e:
            logger.error(f"Error in Azure OpenAI routing: {e}")
            # Fallback to Ollama on error
            logger.info("Falling back to Ollama due to Azure OpenAI error")
            return self._route_ollama(query, context)
    
    def _generate_response(self, query: str, context: List[str], model_config: Dict, intent: IntentType, provider: str = "ollama") -> str:
        """Generate response using the specified model configuration"""
        try:
            # Prepare the prompt based on intent
            prompt = self._prepare_prompt(query, context, intent)
            
            if provider.lower() == "openai" and self.openai_client:
                # Generate response using OpenAI
                response = self.openai_client.chat.completions.create(
                    model=config.config.OPENAI_MODEL,
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=model_config.get('temperature', config.config.OPENAI_TEMPERATURE),
                    max_tokens=model_config.get('max_tokens', config.config.OPENAI_MAX_TOKENS)
                )
                return response.choices[0].message.content
            else:
                # Generate response using Ollama
                response = self.ollama_client.chat(
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
                return f"""Write clean, complete code with proper markdown formatting. Use code blocks and clear explanations.

Context:
{context_text}

Question: {query}

Format your response with:
- **Headers** for main sections
- Code blocks with ```language syntax
- **Bold** for important points
- Bullet points (•) for lists

Provide a complete code solution:"""
            
            elif intent == IntentType.TECHNICAL:
                return f"""You are a technical expert. Answer with proper markdown formatting for clarity and structure.

Context:
{context_text}

Question: {query}

Format your response with:
- **Headers** for main topics
- **Bold** for key terms and important points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a focused technical explanation:"""
            
            elif intent == IntentType.DOCUMENT_QUERY:
                return f"""You are a helpful assistant. Answer with proper markdown formatting based on the provided documents.

Context:
{context_text}

Question: {query}

Format your response with:
- **Headers** for main topics
- **Bold** for key information
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a focused explanation based on the documents:"""
            
            elif intent == IntentType.SUMMARIZE:
                return f"""You are a summarization expert. Create a well-structured summary with proper markdown formatting.

Context:
{context_text}

Question: {query}

Format your response with:
- **Headers** for main sections
- **Bold** for key points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a clear, concise summary:"""
            
            else:  # GENERAL or UNKNOWN
                return f"""Provide a helpful and comprehensive answer with proper markdown formatting.

Context:
{context_text}

Question: {query}

Format your response with:
- **Headers** for main topics
- **Bold** for important points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a detailed response:"""
        else:
            # No context provided
            if intent == IntentType.CODE:
                return f"""Write clean, complete code with proper markdown formatting.

{query}

Format your response with:
- **Headers** for main sections
- Code blocks with ```language syntax
- **Bold** for important points
- Bullet points (•) for lists

Provide a complete code solution:"""
            
            elif intent == IntentType.TECHNICAL:
                return f"""You are a technical expert. Answer with proper markdown formatting.

{query}

Format your response with:
- **Headers** for main topics
- **Bold** for key terms and important points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a focused technical explanation:"""
            
            elif intent == IntentType.SUMMARIZE:
                return f"""You are a summarization expert. Create a well-structured summary with proper markdown formatting.

{query}

Format your response with:
- **Headers** for main sections
- **Bold** for key points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a clear, concise summary:"""
            
            else:
                return f"""Provide a helpful answer with proper markdown formatting.

{query}

Format your response with:
- **Headers** for main topics
- **Bold** for important points
- Bullet points (•) for lists
- Clear paragraph breaks

Provide a helpful response:"""
    
    def _fallback_response(self, query: str, context: List[str], error: str, provider: str = "ollama") -> Dict[str, Any]:
        """Fallback response when routing fails"""
        try:
            if provider.lower() == "openai" and self.openai_client:
                # Try OpenAI fallback
                response = self.openai_client.chat.completions.create(
                    model=config.config.OPENAI_MODEL,
                    messages=[{'role': 'user', 'content': query}],
                    max_tokens=200
                )
                return {
                    'response': response.choices[0].message.content,
                    'intent': 'fallback',
                    'confidence': 0.0,
                    'model_used': config.config.OPENAI_MODEL,
                    'provider': 'openai',
                    'metadata': {'error': error},
                    'explanation': 'Fallback response due to routing error'
                }
            else:
                # Use default Ollama model for fallback
                response = self.ollama_client.chat(
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
                    'provider': 'ollama',
                    'metadata': {'error': error},
                    'explanation': 'Fallback response due to routing error'
                }
            
        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'intent': 'error',
                'confidence': 0.0,
                'model_used': 'none',
                'provider': provider,
                'metadata': {'error': str(e)},
                'explanation': 'Error response'
            }
    
    def get_available_models(self, provider: str = "ollama") -> List[str]:
        """Get list of available models for the specified provider"""
        if provider.lower() == "openai":
            # OpenAI models are predefined
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]
        else:
            # Get Ollama models
            try:
                available_models = self.ollama_client.list()
                return [model['name'] for model in available_models.get('models', [])]
            except Exception as e:
                logger.error(f"Error getting available models: {e}")
                return []
    
    def test_model_connection(self, model_name: str = None, provider: str = "ollama") -> bool:
        """Test connection to a specific model"""
        try:
            if provider.lower() == "openai":
                if not self.openai_client:
                    return False
                # Test OpenAI connection
                response = self.openai_client.chat.completions.create(
                    model=config.config.OPENAI_MODEL,
                    messages=[{'role': 'user', 'content': 'Hello'}],
                    max_tokens=5
                )
                return True
            else:
                # Test Ollama connection
                test_model = model_name or 'llama3.2:1b'
                response = self.ollama_client.chat(
                    model=test_model,
                    messages=[{'role': 'user', 'content': 'Hello'}]
                )
                return True
        except Exception as e:
            logger.error(f"Error testing model {model_name} with provider {provider}: {e}")
            return False
