import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
backend_dir = Path(__file__).parent.parent  # Go up from utils/ to backend/
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure_openai")  # Options: "ollama", "openai", or "azure_openai"
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11435")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "400"))
    
    # Azure OpenAI Configuration (Default)
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", """")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")  # Default deployment name
    AZURE_OPENAI_TEMPERATURE = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.4"))
    AZURE_OPENAI_MAX_TOKENS = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "1000"))
    
    # Multi-Model Configuration
    ENABLE_MULTI_MODEL = os.getenv("ENABLE_MULTI_MODEL", "True").lower() == "true"
    CODE_MODEL = os.getenv("CODE_MODEL", "codellama:7b")
    GENERAL_MODEL = os.getenv("GENERAL_MODEL", "llama3.2:1b")
    TECHNICAL_MODEL = os.getenv("TECHNICAL_MODEL", "llama3.2:1b")
   
    # Application Configuration
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
   
    # Vector Store Configuration - Optimized for better context
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))  # Larger chunks for better context
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 80))  # More overlap for continuity
   
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
    
    # OPTIMIZED Model settings for shorter responses
    MODEL_NAME = "llama3.2:1b"
    TEMPERATURE = 0.3           # Increased from 0.1 for less repetition
    TOP_P = 0.8                # Reduced from 0.9 for more focused responses
    TOP_K = 5                  # Reduced from 10 for more concise answers
    MAX_TOKENS = 150           # Reduced from 256 for shorter responses
    
    # Additional response control parameters
    REPEAT_PENALTY = 1.2       # Penalize repetition
    STOP_SEQUENCES = ["\n\n", ".", "!", "?"]  # Stop at natural break points
    
    # Upload Configuration
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./backend/uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))
   
    # Retrieval Configuration - Optimized for better accuracy
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 4))  # More results for better context
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.4))  # Lower threshold for more inclusive results
    
    # HeyGen API Configuration
    HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")
    HEYGEN_BASE_URL = os.getenv("HEYGEN_BASE_URL", "https://api.heygen.com/v2")
   
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        directories = [
            cls.VECTOR_STORE_PATH,
            cls.UPLOAD_DIR,
            Path(cls.UPLOAD_DIR) / "images"  # Images subdirectory
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize configuration
config = Config()
config.ensure_directories()