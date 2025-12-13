"""Direct test of PDF extraction."""
import sys
from pathlib import Path
from app.services.pdf_service import extract_text, extract_topics
from app.db.session import SessionLocal

# Test PDF extraction
pdf_path = Path("test_data/Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf")
print(f"Testing PDF: {pdf_path.exists()}")

if pdf_path.exists():
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    print("Extracting text...")
    text, ocr_used = extract_text(pdf_bytes)
    print(f"Text length: {len(text)}")
    print(f"OCR used: {ocr_used}")
    print(f"First 200 chars: {text[:200]}")
    
    print("\nExtracting topics...")
    db = SessionLocal()
    try:
        topics = extract_topics(text, db)
        print(f"Topics extracted: {len(topics)}")
        print(f"First topic: {topics[0] if topics else 'None'}")
        print(f"Topic type: {type(topics[0]) if topics else 'None'}")
        if topics and isinstance(topics[0], dict):
            print(f"Topic keys: {list(topics[0].keys())}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


