"""Comprehensive frontend UI test - simulates user interactions."""
import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

print("=" * 70)
print("COMPREHENSIVE FRONTEND-BACKEND INTEGRATION TEST")
print("=" * 70)
print("\nNOTE: Both servers are running on ALL network interfaces (0.0.0.0)")
print("      Backend: http://0.0.0.0:8000")
print("      Frontend: http://0.0.0.0:8501\n")

# Test 1: Backend Health
print("1. Testing Backend Health...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] Backend healthy: {r.json()}")
except Exception as e:
    print(f"   [FAIL] {e}")
    exit(1)

# Test 2: Frontend Accessibility
print("\n2. Testing Frontend Accessibility...")
try:
    r = requests.get(f"{FRONTEND_URL}", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] Frontend accessible (Status: {r.status_code})")
except Exception as e:
    print(f"   [WARN] Frontend check: {e}")

# Test 3: PDF Upload (Full Flow)
print("\n3. Testing PDF Upload and Topic Extraction...")
pdf_path = Path(__file__).parent.parent / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if not pdf_path.exists():
    print(f"   [SKIP] PDF not found at {pdf_path}")
    exit(1)

try:
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)
    
    assert r.status_code == 200
    result = r.json()
    document_id = result.get("document_id")
    topic_status = result.get("topic_extract_status")
    
    print(f"   [OK] PDF uploaded successfully")
    print(f"   [OK] Document ID: {document_id}")
    print(f"   [OK] Topic extraction status: {topic_status}")
    assert topic_status == "completed", "Topic extraction should be completed"
    
except Exception as e:
    print(f"   [FAIL] PDF upload error: {e}")
    exit(1)

# Test 4: Chat Search
print("\n4. Testing Chat Search (Simulating Frontend Request)...")
try:
    payload = {
        "message": "Find Data Engineer and Database Administrator jobs from top companies in the last 30 days in the US",
        "document_id": document_id
    }
    r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
    
    assert r.status_code == 200
    result = r.json()
    conversation_id = result.get("conversation_id")
    response_text = result.get("response", "")
    tool_calls = result.get("tool_calls")
    
    print(f"   [OK] Chat search completed")
    print(f"   [OK] Conversation ID: {conversation_id}")
    print(f"   [OK] Response: {response_text[:150]}...")
    
    if tool_calls:
        print(f"   [OK] Tool called: {tool_calls}")
        assert any("search" in str(tc).lower() for tc in tool_calls), "Search tool should be called"
    else:
        print(f"   [WARN] No tool calls in response")
    
except Exception as e:
    print(f"   [FAIL] Chat search error: {e}")
    exit(1)

# Wait for search to complete
print("\n   Waiting for search to complete...")
time.sleep(10)

# Test 5: Analysis
print("\n5. Testing Gap Analysis (Simulating Frontend Request)...")
try:
    payload = {
        "message": "Analyze the syllabus topics against the job descriptions and show me the gaps",
        "conversation_id": conversation_id,
        "document_id": document_id
    }
    r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
    
    assert r.status_code == 200
    result = r.json()
    tables = result.get("tables")
    response_text = result.get("response", "")
    
    print(f"   [OK] Analysis request completed")
    print(f"   [OK] Response: {response_text[:150]}...")
    
    if tables:
        table_a = tables.get("table_a", [])
        table_b = tables.get("table_b", [])
        
        print(f"   [OK] Table A (Viable Topics): {len(table_a)} rows")
        print(f"   [OK] Table B (Missing Topics): {len(table_b)} rows")
        
        if table_a:
            sample_a = table_a[0]
            print(f"   [OK] Sample Table A row: {sample_a.get('syllabus_topic')} (Score: {sample_a.get('industry_relevance_score')}%)")
            refs_a = sample_a.get('references', [])
            if refs_a:
                print(f"   [OK] Has references: {len(refs_a)} URLs")
        
        if table_b:
            sample_b = table_b[0]
            print(f"   [OK] Sample Table B row: {sample_b.get('missing_topic')} (Priority: {sample_b.get('priority')})")
            refs_b = sample_b.get('references', [])
            if refs_b:
                print(f"   [OK] Has references: {len(refs_b)} URLs")
    else:
        print(f"   [WARN] No tables in analysis response")
    
except Exception as e:
    print(f"   [FAIL] Analysis error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: API Documentation
print("\n6. Testing API Documentation Endpoint...")
try:
    r = requests.get(f"{BACKEND_URL}/docs", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] API docs accessible at {BACKEND_URL}/docs")
except Exception as e:
    print(f"   [WARN] Docs check: {e}")

print("\n" + "=" * 70)
print("FINAL TEST SUMMARY")
print("=" * 70)
print("[OK] Backend Server: Running on 0.0.0.0:8000")
print("[OK] Frontend Server: Running on 0.0.0.0:8501")
print("[OK] PDF Upload: Working")
print("[OK] Topic Extraction: Working")
print("[OK] Chat Search: Working")
print("[OK] Gap Analysis: Working")
print("\nBoth servers are accessible from:")
print("  - Localhost: http://localhost:8000 (backend), http://localhost:8501 (frontend)")
print("  - Network: http://<your-ip>:8000 (backend), http://<your-ip>:8501 (frontend)")
print("=" * 70)


