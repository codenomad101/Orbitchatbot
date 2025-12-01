import fitz  # PyMuPDF
from docx import Document
import tiktoken
from typing import List, Dict, Any
from pathlib import Path
import logging
from utils import config
from PIL import Image
import os

logger = logging.getLogger(__name__)

# OCR for text extraction from images
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("pytesseract not available. OCR functionality will be disabled.")

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = config.config.CHUNK_SIZE
        self.chunk_overlap = config.config.CHUNK_OVERLAP
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file and return extracted text and metadata"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension == '.docx':
                return self._process_docx(file_path)
            elif file_extension == '.txt':
                return self._process_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF file"""
        text_content = ""
        metadata = {
            "file_name": file_path.name,
            "file_type": "pdf",
            "pages": 0
        }
        
        try:
            with fitz.open(file_path) as doc:
                metadata["pages"] = len(doc)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                    text_content += "\n\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
        
        return {
            "text": text_content,
            "metadata": metadata
        }
    
    def _process_docx(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        text_content = ""
        metadata = {
            "file_name": file_path.name,
            "file_type": "docx",
            "paragraphs": 0
        }
        
        try:
            doc = Document(file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
                    text_content += paragraph.text + "\n"
            
            metadata["paragraphs"] = len(paragraphs)
        except Exception as e:
            raise Exception(f"Error reading DOCX: {e}")
        
        return {
            "text": text_content,
            "metadata": metadata
        }
    
    def _process_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from TXT file"""
        metadata = {
            "file_name": file_path.name,
            "file_type": "txt"
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                text_content = file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {e}")
        
        return {
            "text": text_content,
            "metadata": metadata
        }
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks for embedding"""
        if not text.strip():
            return []
        
        chunks = []
        
        # Simple character-based chunking with overlap
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at word boundary if possible
            if end < len(text):
                # Look for the last space within reasonable distance
                for i in range(min(100, self.chunk_size // 10)):
                    if text[end - i] == ' ':
                        end = end - i
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "start_pos": start,
                    "end_pos": end,
                    "token_count": self._count_tokens(chunk_text) if self.tokenizer else len(chunk_text.split())
                }
                
                # Add metadata if provided
                if metadata:
                    chunk["metadata"] = metadata.copy()
                    chunk["metadata"]["chunk_id"] = chunk_id
                
                chunks.append(chunk)
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        # Fallback to word count
        return len(text.split())
    
    def process_image(self, file_path: str) -> Dict[str, Any]:
        """Process an image file and extract text using OCR, along with metadata"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")
        
        metadata = {
            "file_name": file_path.name,
            "file_type": file_path.suffix[1:].lower() if file_path.suffix else "unknown",
            "file_size": file_path.stat().st_size
        }
        
        extracted_text = ""
        ocr_successful = False
        
        # Try to extract image metadata and perform OCR
        try:
            with Image.open(file_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                
                # Perform OCR to extract text from image
                if OCR_AVAILABLE:
                    try:
                        # Extract text using Tesseract OCR
                        extracted_text = pytesseract.image_to_string(img, lang='eng')
                        
                        # Clean up the extracted text
                        if extracted_text:
                            extracted_text = extracted_text.strip()
                            # Remove excessive whitespace
                            extracted_text = ' '.join(extracted_text.split())
                            ocr_successful = True
                            logger.info(f"Successfully extracted {len(extracted_text)} characters from image {file_path.name}")
                        else:
                            logger.info(f"No text found in image {file_path.name} via OCR")
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for {file_path.name}: {ocr_error}")
                        # Continue with metadata-only description
                else:
                    logger.warning("OCR not available. Install pytesseract and Tesseract OCR to enable text extraction.")
                
                # Create description combining OCR text and metadata
                description_parts = []
                
                # Add OCR extracted text if available
                if extracted_text:
                    description_parts.append(extracted_text)
                
                # Add metadata information
                metadata_info = f"Image file: {file_path.name}. "
                metadata_info += f"Dimensions: {img.width}x{img.height} pixels. "
                metadata_info += f"Format: {img.format or 'unknown'}. "
                
                # Add filename as searchable text
                filename_without_ext = file_path.stem
                metadata_info += f"Filename: {filename_without_ext}."
                
                # Combine OCR text and metadata
                if description_parts:
                    # If OCR text exists, add metadata as additional context
                    description = "\n\n".join(description_parts) + "\n\n" + metadata_info
                else:
                    # If no OCR text, use metadata only
                    description = metadata_info
                
                # Add OCR status to metadata
                metadata["ocr_performed"] = OCR_AVAILABLE
                metadata["ocr_successful"] = ocr_successful
                metadata["text_extracted_length"] = len(extracted_text) if extracted_text else 0
                
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            # Fallback description
            description = f"Image file: {file_path.name}"
            metadata["ocr_performed"] = False
            metadata["ocr_successful"] = False
        
        return {
            "text": description,
            "metadata": metadata
        }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
            "supported": file_path.suffix.lower() in ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        }