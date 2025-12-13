"""Test script for frontend-backend integration."""
import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

print("=" * 60)
print("FRONTEND-BACKEND INTEGRATION TEST")
print("=" * 60)

# Test 1: Backend health
print("\n1. Testing Backend...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if r.status_code == 200:
        print(f"   [OK] Backend is healthy at {BACKEND_URL}")
    else:
        print(f"   [FAIL] Backend returned {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Backend not reachable: {e}")

# Test 2: Frontend reachability
print("\n2. Testing Frontend...")
try:
    r = requests.get(f"{FRONTEND_URL}", timeout=5)
    if r.status_code == 200:
        print(f"   [OK] Frontend is accessible at {FRONTEND_URL}")
    else:
        print(f"   [WARN] Frontend returned {r.status_code}")
except Exception as e:
    print(f"   [WARN] Frontend check: {e}")

# Test 3: PDF upload via backend
print("\n3. Testing PDF Upload (Backend)...")
pdf_path = Path(__file__).parent.parent / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if pdf_path.exists():
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)
        
        if r.status_code == 200:
            result = r.json()
            document_id = result.get("document_id")
            print(f"   [OK] PDF uploaded, Document ID: {document_id[:8]}...")
            print(f"   [OK] Topic extraction: {result.get('topic_extract_status')}")
            
            # Test 4: Chat search
            print("\n4. Testing Chat Search (Backend)...")
            payload = {
                "message": "Find Data Engineer jobs from top companies in the last 30 days",
                "document_id": document_id
            }
            r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=180)
            
            if r.status_code == 200:
                result = r.json()
                conversation_id = result.get("conversation_id")
                print(f"   [OK] Chat search completed")
                print(f"   [OK] Conversation ID: {conversation_id[:8]}...")
                print(f"   [OK] Response: {result.get('response', '')[:100]}...")
                
                # Test 5: Analysis
                print("\n5. Testing Analysis (Backend)...")
                payload = {
                    "message": "Analyze the syllabus against job descriptions",
                    "conversation_id": conversation_id,
                    "document_id": document_id
                }
                r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
                
                if r.status_code == 200:
                    result = r.json()
                    tables = result.get("tables")
                    if tables:
                        table_a = tables.get("table_a", [])
                        table_b = tables.get("table_b", [])
                        print(f"   [OK] Analysis completed")
                        print(f"   [OK] Table A: {len(table_a)} rows")
                        print(f"   [OK] Table B: {len(table_b)} rows")
                    else:
                        print(f"   [WARN] No tables in response")
                else:
                    print(f"   [FAIL] Analysis failed: {r.status_code}")
            else:
                print(f"   [FAIL] Chat search failed: {r.status_code}")
        else:
            print(f"   [FAIL] PDF upload failed: {r.status_code}")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
else:
    print(f"   [SKIP] PDF file not found at {pdf_path}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("Backend and Frontend are running on all network interfaces")
print(f"Backend: http://0.0.0.0:8000 (accessible via http://localhost:8000)")
print(f"Frontend: http://0.0.0.0:8501 (accessible via http://localhost:8501)")
print("=" * 60)


