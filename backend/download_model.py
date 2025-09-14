#!/usr/bin/env python3
"""
Script to download the embedding model with SSL bypass
"""

import ssl
import os
import urllib3

# SSL bypass
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment variables
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'

try:
    from sentence_transformers import SentenceTransformer
    
    print("Downloading embedding model...")
    model = SentenceTransformer(
        'all-MiniLM-L6-v2', 
        cache_folder='./model_cache'
    )
    print("Model downloaded successfully!")
    print(f"Model dimension: {model.get_sentence_embedding_dimension()}")
    
    # Test encoding
    test_embedding = model.encode(["Hello world"])
    print(f"Test encoding successful. Shape: {test_embedding.shape}")
    
except Exception as e:
    print(f"Error downloading model: {e}")
    print("You may need to use the dummy model approach or try a different network.")