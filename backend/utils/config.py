import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11435")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    # Multi-Model Configuration
    ENABLE_MULTI_MODEL = os.getenv("ENABLE_MULTI_MODEL", "True").lower() == "true"
    CODE_MODEL = os.getenv("CODE_MODEL", "codellama:7b")
    GENERAL_MODEL = os.getenv("GENERAL_MODEL", "llama3.2:1b")
    TECHNICAL_MODEL = os.getenv("TECHNICAL_MODEL", "llama3.2:1b")
   
    # Application Configuration
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
   
    # Vector Store Configuration
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 200))  # Even smaller chunks for more focused content
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 30))  # Minimal overlap
   
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
   
    # Retrieval Configuration - Optimized for focused responses
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))  # Fewer, more relevant results
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.5))  # Higher threshold for more relevant results
   
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        directories = [
            cls.VECTOR_STORE_PATH,
            cls.UPLOAD_DIR
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize configuration
config = Config()
config.ensure_directories()