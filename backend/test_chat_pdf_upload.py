"""Test PDF upload through chat interface."""
import requests
import json
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

print("=" * 70)
print("TEST: PDF Upload Through Chat Interface")
print("=" * 70)
print(f"Backend: {BACKEND_URL}\n")

# Test 1: Health check
print("1. Testing Backend Health...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] Backend healthy: {r.json()}")
except Exception as e:
    print(f"   [FAIL] Backend not responding: {e}")
    exit(1)

# Test 2: Upload PDF via /pdf endpoint (simulating chat upload)
print("\n2. Uploading PDF (as chat would do)...")
pdf_path = Path(__file__).parent / "test_data" / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"

if not pdf_path.exists():
    print(f"   [FAIL] PDF not found at {pdf_path}")
    exit(1)

try:
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)
    
    if r.status_code == 200:
        result = r.json()
        document_id = result["document_id"]
        print(f"   [OK] PDF uploaded successfully")
        print(f"   Document ID: {document_id[:8]}...")
        print(f"   Topic extraction: {result['topic_extract_status']}")
        
        # Test 3: Chat with the uploaded document
        print("\n3. Testing chat with uploaded document...")
        conversation_id = None
        
        test_messages = [
            "I just uploaded a PDF. Can you tell me what topics were extracted?",
            "What can I do with this document?",
            "Can you analyze it against job descriptions?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Turn {i}: {message}")
            payload = {
                "message": message,
                "conversation_id": conversation_id,
                "document_id": document_id
            }
            
            r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
            
            if r.status_code == 200:
                result = r.json()
                conversation_id = result["conversation_id"]
                response = result.get("response", "")[:200]
                print(f"   Response: {response}...")
                
                if result.get("document_id"):
                    print(f"   [OK] Document ID in response: {result['document_id'][:8]}...")
            else:
                print(f"   [FAIL] Status {r.status_code}: {r.text}")
                break
        
        print("\n   [OK] Chat with PDF document works!")
        
    else:
        print(f"   [FAIL] Upload failed: {r.status_code} - {r.text}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

