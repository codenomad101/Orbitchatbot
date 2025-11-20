import ollama
import httpx
from typing import List, Dict, Any
from utils import config
from services.model_router import ModelRouter

class LLMHandler:
    def __init__(self):
        self.client = ollama.Client(host=config.config.OLLAMA_HOST)
        self.model = config.config.OLLAMA_MODEL
        self.model_router = ModelRouter()

    async def generate_response(self, prompt: str, context: List[str] = None) -> str:
        """Generate response using intelligent model routing"""
        try:
            # Use the model router for intelligent routing
            result = self.model_router.route_query(prompt, context)
            return result['response']
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Sorry, I encountered an error while generating the response: {str(e)}"
    
    async def generate_response_with_metadata(self, prompt: str, context: List[str] = None, provider: str = None) -> Dict[str, Any]:
        """Generate response with full metadata including intent classification"""
        try:
            # Use the model router for intelligent routing
            result = self.model_router.route_query(prompt, context, provider=provider)
            return result
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'response': f"Sorry, I encountered an error while generating the response: {str(e)}",
                'intent': 'error',
                'confidence': 0.0,
                'model_used': 'none',
                'provider': provider or 'unknown',
                'metadata': {'error': str(e)},
                'explanation': 'Error response'
            }
    
    async def test_connection(self) -> bool:
        """Test if Ollama service is available"""
        try:
            # Try to list available models
            models = self.client.list()
            return True
        except Exception as e:
            print(f"Ollama connection test failed: {e}")
            return False
    
    async def generate_embedding_prompt(self, text: str) -> str:
        """Generate embeddings using the LLM (if supported)"""
        # Note: Not all models support embeddings directly
        # This is a placeholder for future implementation
        return text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            models = self.client.list()
            current_model = None
            for model in models.get('models', []):
                if model['name'] == self.model:
                    current_model = model
                    break
            return {
                "model_name": self.model,
                "available": current_model is not None,
                "model_info": current_model
            }
        except Exception as e:
            return {
                "model_name": self.model,
                "available": False,
                "error": str(e)
            }