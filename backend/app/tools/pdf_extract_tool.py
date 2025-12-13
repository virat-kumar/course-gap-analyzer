"""PDF text extraction tool."""
import pdfplumber
from pathlib import Path
from typing import Optional, Tuple


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, bool]:
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (extracted_text, ocr_used)
        - extracted_text: Full text content
        - ocr_used: Whether OCR was needed (currently always False)
    """
    text_parts = []
    ocr_used = False
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    # Page has no extractable text - might need OCR
                    # For now, just note it
                    text_parts.append(f"[Page {page_num}: No text content found]")
        
        full_text = "\n\n".join(text_parts)
        
        # If no text extracted, might need OCR in future
        # For now, we'll just return what we have
        if not full_text.strip():
            ocr_used = True  # Would use OCR here
        
        return full_text, ocr_used
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_bytes(pdf_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF bytes (for uploaded files).
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Tuple of (extracted_text, ocr_used)
    """
    import io
    
    text_parts = []
    ocr_used = False
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    text_parts.append(f"[Page {page_num}: No text content found]")
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            ocr_used = True
        
        return full_text, ocr_used
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF bytes: {str(e)}")


