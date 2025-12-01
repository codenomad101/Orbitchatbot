import ssl_bypass  # Import this FIRST, before any other imports
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import shutil
import os
import time
import re
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import unquote
import asyncio
import ssl
import os
import urllib3
import httpx
import json

# Disable SSL warnings and verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


# Local imports
from services.document_processor import DocumentProcessor
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from models.llm_handler import LLMHandler
from utils.config import config

# Database imports
from database.config import init_database, check_database_connection, get_db
from database.services import UserService, DocumentService, SearchService, LogService
from database.models import User, Document
from sqlalchemy.orm import Session
from sqlalchemy import func

# Auth imports
from auth.db_auth_handler import get_auth_handler
from auth.models import UserCreate, UserLogin, UserResponse, Token, UserRoleUpdate, DocumentResponse, SearchQueryResponse
from auth.dependencies import get_current_active_user, get_admin_user, get_optional_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLAMA 4 RAG API",
    description="RAG system with LLAMA 4 for document Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
document_processor = None
embedding_service = None
vector_store = None
llm_handler = None

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    provider: Optional[str] = None  # "ollama" or "openai", defaults to config.LLM_PROVIDER

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str
    intent: Optional[str] = None  # Add intent field
    images: Optional[List[Dict[str, Any]]] = []  # List of image URLs and metadata

class HeyGenVideoRequest(BaseModel):
    video_inputs: List[Dict[str, Any]]
    test: Optional[bool] = False

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global document_processor, embedding_service, vector_store, llm_handler
    
    try:
        logger.info("Initializing services...")
        
        # Initialize database
        logger.info("Initializing database...")
        if not check_database_connection():
            logger.error("Database connection failed!")
            raise Exception("Database connection failed")
        
        init_database()
        logger.info("Database initialized successfully")
        
        # Create default admin user
        from database.config import SessionLocal
        db = SessionLocal()
        try:
            auth_handler = get_auth_handler(db)
            auth_handler.create_default_admin()
        finally:
            db.close()
        
        # Initialize services
        document_processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        
        # Get embedding dimension for vector store
        embedding_dim = embedding_service.get_embedding_dimension()
        vector_store = VectorStore(dimension=embedding_dim)
        
        llm_handler = LLMHandler()
        
        # Test LLM connection
        connection_ok = await llm_handler.test_connection()
        if not connection_ok:
            logger.warning("Could not connect to Ollama. Please ensure Ollama is running.")
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLAMA 4 RAG API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        services_status = {
            "document_processor": document_processor is not None,
            "embedding_service": embedding_service is not None,
            "vector_store": vector_store is not None,
            "llm_handler": llm_handler is not None
        }
        
        # Test LLM connection
        llm_connection = await llm_handler.test_connection() if llm_handler else False
        
        # Get vector store stats
        vector_stats = vector_store.get_stats() if vector_store else {}
        
        return {
            "status": "healthy",
            "services": services_status,
            "llm_connection": llm_connection,
            "vector_store_stats": vector_stats,
            "config": {
                "model": config.OLLAMA_MODEL,
                "embedding_model": config.EMBEDDING_MODEL
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document (Admin only)"""
    try:
        # Validate file type - support documents and images
        allowed_document_extensions = {'.pdf', '.docx', '.txt'}
        allowed_image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        allowed_extensions = allowed_document_extensions | allowed_image_extensions
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed documents: {', '.join(allowed_document_extensions)}. Allowed images: {', '.join(allowed_image_extensions)}"
            )
        
        is_image = file_extension in allowed_image_extensions
        
        # Check file size
        if file.size > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {config.MAX_FILE_SIZE} bytes"
            )
        
        # Check for duplicate filename
        document_service = DocumentService(db)
        existing_document = document_service.get_document_by_filename(file.filename)
        if existing_document:
            raise HTTPException(
                status_code=400,
                detail=f"Document with filename '{file.filename}' already exists. Please use a different filename or delete the existing document first."
            )
        
        # Save uploaded file - use different directories for images vs documents
        if is_image:
            # Store images in a separate directory and keep them
            image_dir = Path(config.UPLOAD_DIR) / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            file_path = image_dir / file.filename
        else:
            file_path = Path(config.UPLOAD_DIR) / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create document record in database
        document = document_service.create_document(
            filename=file.filename,
            original_filename=file.filename,
            file_type=file_extension[1:],  # Remove the dot
            file_size=file.size,
            upload_path=str(file_path),
            uploaded_by=current_user.id
        )
        
        if not document:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        # Process file in background (documents get processed, images get metadata extracted)
        if is_image:
            background_tasks.add_task(process_image_background, str(file_path), document.id, db)
        else:
            background_tasks.add_task(process_document_background, str(file_path), document.id, db)
        
        # Log the upload
        log_service = LogService(db)
        log_service.create_log(
            action="document_uploaded",
            user_id=current_user.id,
            resource_type="document",
            resource_id=document.id,
            details={"filename": file.filename, "file_size": file.size}
        )
        
        return DocumentResponse.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

async def process_document_background(file_path: str, document_id: int, db: Session):
    """Background task to process uploaded document"""
    try:
        logger.info(f"Processing document: {file_path}")
        
        # Update document status to processing
        document_service = DocumentService(db)
        document_service.update_document_status(document_id, "processing")
        
        # Process document
        result = document_processor.process_file(file_path)
        text = result["text"]
        metadata = result["metadata"]
        
        # Create chunks
        chunks = document_processor.chunk_text(text, metadata)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        chunks_with_embeddings = embedding_service.encode_chunks(chunks)
        logger.info("Generated embeddings for chunks")
        
        # Add to vector store
        vector_store.add_documents(chunks_with_embeddings)
        logger.info("Added chunks to vector store")
        
        # Update document status and chunk count
        document_service.update_document_status(document_id, "completed")
        document_service.update_document_chunks(document_id, len(chunks))
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        logger.info(f"Successfully processed document: {Path(file_path).name}")
        
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {e}")
        # Update document status to failed
        document_service = DocumentService(db)
        document_service.update_document_status(document_id, "failed", str(e))

async def process_image_background(file_path: str, document_id: int, db: Session):
    """Background task to process uploaded image"""
    try:
        logger.info(f"Processing image: {file_path}")
        
        # Update document status to processing
        document_service = DocumentService(db)
        document_service.update_document_status(document_id, "processing")
        
        # Process image - extract metadata and create description
        result = document_processor.process_image(file_path)
        text = result.get("text", "")
        metadata = result.get("metadata", {})
        
        # Create chunks from image description/metadata
        if text:
            chunks = document_processor.chunk_text(text, metadata)
            logger.info(f"Created {len(chunks)} chunks from image")
            
            if chunks:
                # Generate embeddings
                chunks_with_embeddings = embedding_service.encode_chunks(chunks)
                logger.info("Generated embeddings for image chunks")
                
                # Add to vector store
                vector_store.add_documents(chunks_with_embeddings)
                logger.info("Added image chunks to vector store")
                
                # Update document status and chunk count
                document_service.update_document_status(document_id, "completed")
                document_service.update_document_chunks(document_id, len(chunks))
            else:
                # No text extracted, but image is stored
                document_service.update_document_status(document_id, "completed")
                document_service.update_document_chunks(document_id, 0)
        else:
            # No text extracted, but image is stored
            document_service.update_document_status(document_id, "completed")
            document_service.update_document_chunks(document_id, 0)
        
        # Images are kept (not deleted like documents)
        logger.info(f"Successfully processed image: {Path(file_path).name}")
        
    except Exception as e:
        logger.error(f"Error processing image {file_path}: {e}")
        # Update document status to failed
        document_service = DocumentService(db)
        document_service.update_document_status(document_id, "failed", str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Query the document collection"""
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        top_k = request.top_k or config.TOP_K_RESULTS
        
        # Create search query record
        search_service = SearchService(db)
        search_query = search_service.create_search_query(current_user.id, question)
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = embedding_service.encode_single_text(question)
        
        # Search vector store
        search_results = vector_store.search(query_embedding, top_k=top_k)
        
        if not search_results:
            response_time = int((time.time() - start_time) * 1000)
            search_service.update_search_response(
                search_query.id,
                "I couldn't find any relevant information in the uploaded documents to answer your question.",
                [],
                response_time
            )
            
            return QueryResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                sources=[],
                query=question,
                intent="unknown"
            )
        
        # Extract context from search results
        context_texts = []
        sources = []
        images = []
        seen_image_files = set()  # Track images to avoid duplicates
        seen_document_ids = set()  # Track document IDs to get all related images
        
        # First pass: collect context, sources, and identify related documents
        for result in search_results:
            context_texts.append(result["text"])
            file_name = result.get("metadata", {}).get("file_name", "Unknown")
            file_type = result.get("metadata", {}).get("file_type", "")
            
            sources.append({
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "title": file_name,
                "score": result.get("similarity_score", 0),
                "similarity_score": result.get("similarity_score", 0),
                "chunk_id": result.get("chunk_id", 0),
                "file_name": file_name
            })
            
            # Track document IDs from metadata if available
            metadata = result.get("metadata", {})
            if "document_id" in metadata:
                seen_document_ids.add(metadata["document_id"])
            
            # Check if this result is from an image file
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
            is_image_file = file_type.lower() in [ext[1:] for ext in image_extensions] or \
                           any(file_name.lower().endswith(ext) for ext in image_extensions)
            
            if is_image_file:
                # This is an image - add to images list if not already added
                if file_name not in seen_image_files:
                    seen_image_files.add(file_name)
                    # Get document to find upload path
                    doc_service = DocumentService(db)
                    document = doc_service.get_document_by_filename(file_name)
                    
                    # If exact match fails, try case-insensitive search
                    if not document:
                        # Try to find document with case-insensitive filename match
                        document = db.query(Document).filter(
                            func.lower(Document.filename) == file_name.lower()
                        ).first()
                        if document:
                            logger.info(f"Found image document via case-insensitive search: {file_name} -> {document.filename}")
                    
                    if document and document.upload_path:
                        # Verify file exists
                        if Path(document.upload_path).exists():
                            seen_document_ids.add(document.id)
                            image_url = f"/api/images/{document.id}/{file_name}"
                            images.append({
                                "url": image_url,
                                "filename": file_name,
                                "title": file_name,
                                "score": result.get("similarity_score", 0)
                            })
                            logger.info(f"✓ Added image to response: {file_name} (ID: {document.id}, URL: {image_url})")
                        else:
                            logger.warning(f"✗ Image file not found on disk: {document.upload_path} for {file_name}")
                    else:
                        if not document:
                            logger.warning(f"✗ Document not found in database for image: {file_name}")
                        elif not document.upload_path:
                            logger.warning(f"✗ Document {document.id} has no upload_path for image: {file_name}")
        
        # Second pass: Get additional images from documents that appeared in search results
        # This ensures we get all images from documents that are relevant to the query
        doc_service = DocumentService(db)
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        
        # Get unique document IDs and filenames from search results
        related_document_ids = set()
        related_filenames = set()
        for result in search_results:
            metadata = result.get("metadata", {})
            if "document_id" in metadata:
                related_document_ids.add(metadata["document_id"])
            file_name = metadata.get("file_name", "")
            if file_name:
                related_filenames.add(file_name)
        
        # Get images from documents that are related to the search results
        # First, try to get documents by ID
        for doc_id in related_document_ids:
            document = doc_service.get_document_by_id(doc_id)
            if document:
                file_type = document.file_type.lower() if document.file_type else ""
                is_image = file_type in [ext[1:] for ext in image_extensions] or \
                          any(document.filename.lower().endswith(ext) for ext in image_extensions)
                
                if is_image and document.upload_path and document.filename not in seen_image_files:
                    if Path(document.upload_path).exists():
                        seen_image_files.add(document.filename)
                        image_url = f"/api/images/{document.id}/{document.filename}"
                        images.append({
                            "url": image_url,
                            "filename": document.filename,
                            "title": document.filename,
                            "score": 0.4  # Score for images from related documents
                        })
        
        # Also get images by filename from search results
        for filename in related_filenames:
            if filename not in seen_image_files:
                document = doc_service.get_document_by_filename(filename)
                
                # If exact match fails, try case-insensitive search
                if not document:
                    document = db.query(Document).filter(
                        func.lower(Document.filename) == filename.lower()
                    ).first()
                
                if document:
                    file_type = document.file_type.lower() if document.file_type else ""
                    is_image = file_type in [ext[1:] for ext in image_extensions] or \
                              any(filename.lower().endswith(ext) for ext in image_extensions)
                    
                    if is_image and document.upload_path:
                        if Path(document.upload_path).exists():
                            seen_image_files.add(filename)
                            image_url = f"/api/images/{document.id}/{filename}"
                            images.append({
                                "url": image_url,
                                "filename": filename,
                                "title": filename,
                                "score": 0.4
                            })
                            logger.info(f"Added related image to response: {filename} (ID: {document.id})")
        
        # Sort images by score (highest first) to show most relevant images first
        images.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Limit to top 15 images to avoid overwhelming the response
        images = images[:15]
        
        logger.info(f"Collected {len(images)} images from search results before LLM generation")
        if images:
            logger.info(f"Image filenames: {[img.get('filename', 'unknown') for img in images]}")
        
        # Generate answer using LLM with metadata
        provider = request.provider  # Get provider from request, or None to use config default
        llm_result = await llm_handler.generate_response_with_metadata(question, context_texts, provider=provider)
        answer = llm_result["response"]
        intent = llm_result.get("intent", "general")
        
        logger.info(f"LLM generated response. Current images count: {len(images)}")
        
        # Extract image filenames mentioned in the LLM response and add them to images array
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
        
        # Pattern to find image filenames in the text (handles spaces and special characters)
        # Matches: "filename.png", "filename with spaces.png", "lmkv2 abd lmkv3.png", etc.
        # Pattern matches: word characters, spaces, hyphens, underscores, dots, followed by image extension
        image_pattern = r'([\w\s\-_.]+\.(?:jpg|jpeg|png|gif|webp|bmp|svg))'
        mentioned_images = re.findall(image_pattern, answer, re.IGNORECASE)
        
        # Also try to find quoted filenames: "filename.png" or 'filename.png'
        quoted_pattern = r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|bmp|svg))["\']'
        quoted_images = re.findall(quoted_pattern, answer, re.IGNORECASE)
        mentioned_images.extend(quoted_images)
        
        # Remove duplicates while preserving order
        mentioned_images = list(dict.fromkeys(mentioned_images))
        
        logger.info(f"Found {len(mentioned_images)} image filenames mentioned in response: {mentioned_images}")
        
        # Look up mentioned images in the database and add them if not already included
        for mentioned_filename in mentioned_images:
            mentioned_filename = mentioned_filename.strip()
            if mentioned_filename and mentioned_filename.lower() not in [img.get("filename", "").lower() for img in images]:
                # Try to find the document
                document = doc_service.get_document_by_filename(mentioned_filename)
                
                # If exact match fails, try case-insensitive search
                if not document:
                    document = db.query(Document).filter(
                        func.lower(Document.filename) == mentioned_filename.lower()
                    ).first()
                
                if document:
                    file_type = document.file_type.lower() if document.file_type else ""
                    is_image = file_type in [ext[1:] for ext in image_extensions] or \
                              any(mentioned_filename.lower().endswith(ext) for ext in image_extensions)
                    
                    if is_image and document.upload_path:
                        if Path(document.upload_path).exists():
                            image_url = f"/api/images/{document.id}/{mentioned_filename}"
                            images.append({
                                "url": image_url,
                                "filename": mentioned_filename,
                                "title": mentioned_filename,
                                "score": 0.2  # Lower score for images mentioned in text
                            })
                            logger.info(f"Added mentioned image to response: {mentioned_filename} (ID: {document.id})")
                        else:
                            logger.warning(f"Mentioned image file not found on disk: {document.upload_path}")
                    else:
                        logger.warning(f"Mentioned file is not an image or has no upload_path: {mentioned_filename}")
                else:
                    logger.warning(f"Mentioned image not found in database: {mentioned_filename}")
        
        # Update search query with response
        response_time = int((time.time() - start_time) * 1000)
        search_service.update_search_response(search_query.id, answer, sources, response_time)
        
        # Log the query
        log_service = LogService(db)
        log_service.create_log(
            action="document_query",
            user_id=current_user.id,
            resource_type="search",
            resource_id=search_query.id,
            details={"query": question, "response_time_ms": response_time}
        )
        
        logger.info(f"Returning response with {len(images)} images")
        if images:
            logger.info(f"Images being returned: {[(img.get('filename'), img.get('url')) for img in images]}")
        else:
            logger.warning("No images found in response - check if images exist in search results or database")
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=question,
            intent=intent,
            images=images
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/images/{document_id}/{filename:path}")
async def get_image(
    document_id: int,
    filename: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Serve uploaded images"""
    try:
        # FastAPI automatically URL-decodes path parameters, but let's be explicit
        decoded_filename = unquote(filename)
        
        logger.info(f"Image request: document_id={document_id}, filename='{filename}', decoded='{decoded_filename}'")
        
        document_service = DocumentService(db)
        document = document_service.get_document_by_id(document_id)
        
        if not document:
            logger.warning(f"Document not found: ID={document_id}")
            raise HTTPException(status_code=404, detail=f"Image not found: Document ID {document_id} does not exist")
        
        logger.info(f"Found document: ID={document.id}, filename='{document.filename}', upload_path='{document.upload_path}'")
        
        # Verify filename matches (compare with decoded filename, case-insensitive)
        # Use case-insensitive comparison to handle filename variations
        if document.filename.lower() != decoded_filename.lower():
            logger.warning(f"Filename mismatch: stored='{document.filename}', requested='{decoded_filename}'")
            raise HTTPException(
                status_code=404, 
                detail=f"Image not found: Filename mismatch. Stored: '{document.filename}', Requested: '{decoded_filename}'"
            )
        else:
            logger.info(f"Filename matches: '{document.filename}' == '{decoded_filename}'")
        
        # Check if file exists
        if not document.upload_path:
            logger.error(f"Document {document_id} has no upload_path")
            raise HTTPException(status_code=404, detail="Image file path not configured")
        
        file_path = Path(document.upload_path)
        if not file_path.exists():
            logger.error(f"Image file not found on disk: {document.upload_path}")
            raise HTTPException(status_code=404, detail=f"Image file not found: {document.upload_path}")
        
        logger.info(f"Serving image: {document.upload_path}")
        
        # Return the image file
        return FileResponse(
            document.upload_path,
            media_type=f"image/{Path(filename).suffix[1:].lower()}" if Path(filename).suffix else "image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """List information about stored documents (Admin only)"""
    try:
        document_service = DocumentService(db)
        documents = document_service.get_all_documents()
        
        # Log the action
        log_service = LogService(db)
        log_service.create_log(
            action="documents_listed",
            user_id=current_user.id,
            resource_type="document"
        )
        
        return [DocumentResponse.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: int, 
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a specific document and its chunks (Admin only)"""
    try:
        document_service = DocumentService(db)
        document = document_service.get_document_by_id(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from vector store
        deleted_count = vector_store.delete_by_filename(document.filename)
        
        # Delete from database
        success = document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document from database")
        
        # Log the deletion
        log_service = LogService(db)
        log_service.create_log(
            action="document_deleted",
            user_id=current_user.id,
            resource_type="document",
            resource_id=document_id,
            details={"filename": document.filename, "chunks_deleted": deleted_count}
        )
        
        return {
            "message": f"Deleted document: {document.filename}",
            "chunks_deleted": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

@app.get("/models/info")
async def get_model_info():
    """Get information about loaded models"""
    try:
        llm_info = llm_handler.get_model_info() if llm_handler else {}
        embedding_info = embedding_service.get_model_info() if embedding_service else {}
        
        return {
            "llm_model": llm_info,
            "embedding_model": embedding_info
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Model info error: {str(e)}")

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        auth_handler = get_auth_handler(db)
        success = auth_handler.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Return user data without password
        new_user = auth_handler.get_user_by_username(user_data.username)
        return UserResponse.model_validate(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    try:
        auth_handler = get_auth_handler(db)
        user = auth_handler.authenticate_user(user_credentials.username, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = auth_handler.create_access_token(
            data={"sub": user.id, "role": user.role}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@app.get("/auth/users", response_model=List[UserResponse])
async def list_users(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """List all users (admin only)"""
    try:
        auth_handler = get_auth_handler(db)
        users = auth_handler.get_all_users()
        return [UserResponse.model_validate(user) for user in users]
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")

@app.put("/auth/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    try:
        auth_handler = get_auth_handler(db)
        success = auth_handler.update_user_role(user_id, role_update.role)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User role updated to {role_update.role}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")

@app.put("/auth/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    try:
        auth_handler = get_auth_handler(db)
        success = auth_handler.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User has been deactivated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error deactivating user: {str(e)}")

@app.post("/auth/users/create", response_model=UserResponse)
async def create_user_by_admin(
    user_data: UserCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)"""
    try:
        auth_handler = get_auth_handler(db)
        success = auth_handler.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Return user data without password
        new_user = auth_handler.get_user_by_username(user_data.username)
        
        # Log the user creation by admin
        log_service = LogService(db)
        log_service.create_log(
            action="user_created_by_admin",
            user_id=admin_user.id,
            resource_type="user",
            resource_id=new_user.id,
            details={"created_user": user_data.username, "role": user_data.role}
        )
        
        return UserResponse.model_validate(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"User creation error: {str(e)}")

# Additional endpoints for analytics and search history
@app.get("/search/history", response_model=List[SearchQueryResponse])
async def get_search_history(
    current_user: User = Depends(get_current_active_user),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's search history"""
    try:
        search_service = SearchService(db)
        queries = search_service.get_user_search_history(current_user.id, limit)
        
        # Convert to response format with query and answer fields for frontend compatibility
        results = []
        for query in queries:
            query_dict = {
                "id": query.id,
                "query_text": query.query_text,
                "query": query.query_text,  # Add query field for frontend
                "response_text": query.response_text,
                "answer": query.response_text,  # Add answer field for frontend
                "response_time_ms": query.response_time_ms,
                "created_at": query.created_at
            }
            results.append(SearchQueryResponse.model_validate(query_dict))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting search history: {str(e)}")

@app.get("/analytics/stats")
async def get_analytics_stats(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get system analytics (Admin only)"""
    try:
        search_service = SearchService(db)
        document_service = DocumentService(db)
        user_service = UserService(db)
        
        search_stats = search_service.get_search_stats()
        total_documents = len(document_service.get_all_documents())
        total_users = len(user_service.get_all_users())
        
        return {
            "search_stats": search_stats,
            "total_documents": total_documents,
            "total_users": total_users,
            "vector_store_stats": vector_store.get_stats() if vector_store else {}
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@app.get("/logs/system")
async def get_system_logs(
    admin_user: User = Depends(get_admin_user),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get system logs (Admin only)"""
    try:
        log_service = LogService(db)
        logs = log_service.get_system_logs(limit)
        
        return [
            {
                "id": log.id,
                "action": log.action,
                "user_id": log.user_id,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
        
    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system logs: {str(e)}")

# HeyGen API Proxy Endpoints (to avoid CORS issues)
@app.post("/heygen/video/generate")
async def heygen_generate_video(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Proxy endpoint for HeyGen video generation (avoids CORS)"""
    if not hasattr(config, 'HEYGEN_API_KEY') or not config.HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="HeyGen API key not configured")
    
    try:
        # Get JSON payload from frontend
        payload = await request.json()
        logger.info(f"HeyGen video generation request received: {json.dumps(payload, indent=2)[:500]}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{config.HEYGEN_BASE_URL}/video/generate",
                headers={
                    "X-Api-Key": config.HEYGEN_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0  # Wait up to 30s for HeyGen to accept
            )
            
            logger.info(f"HeyGen generate response status: {response.status_code}")
            logger.info(f"HeyGen generate response: {response.text[:500]}")
            
            # Return HeyGen's response exactly as is
            if response.status_code != 200:
                logger.error(f"HeyGen API error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            response_data = response.json()
            # Log the video_id or task_id if present
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    data = response_data['data']
                    if 'video_id' in data:
                        logger.info(f"Video generation started, video_id: {data['video_id']}")
                    if 'task_id' in data:
                        logger.info(f"Video generation started, task_id: {data['task_id']}")
            
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HeyGen API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Error calling HeyGen API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/heygen/video/{video_id}")
async def heygen_get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Proxy endpoint for HeyGen video status (avoids CORS)
    Uses the correct HeyGen API format: /v1/video_status.get?video_id={video_id}
    """
    logger.info(f"Checking video status for video_id: {video_id}")
    
    if not hasattr(config, 'HEYGEN_API_KEY') or not config.HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="HeyGen API key not configured")
    
    headers = {
        "X-Api-Key": config.HEYGEN_API_KEY,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use the correct endpoint with query parameter (not path parameter)
            url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
            logger.info(f"Calling HeyGen endpoint: {url}")
            
            response = await client.get(url, headers=headers)
            logger.info(f"HeyGen response status: {response.status_code}")
            logger.info(f"HeyGen response text: {response.text[:500]}")
            
            if response.status_code == 200:
                return response.json()
            
            # Handle error responses
            logger.error(f"HeyGen API returned {response.status_code} for video_id: {video_id}")
            logger.error(f"Response text: {response.text}")
            
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            
            raise HTTPException(
                status_code=response.status_code, 
                detail={
                    "error": f"HeyGen API returned {response.status_code}",
                    "message": error_detail,
                    "video_id": video_id
                }
            )
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"HeyGen API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail={
                "error": "HeyGen API error",
                "status_code": e.response.status_code,
                "message": e.response.text[:500]
            }
        )
    except Exception as e:
        logger.error(f"Error calling HeyGen API: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.APP_HOST, 
        port=config.APP_PORT,
        log_level="info"
    )