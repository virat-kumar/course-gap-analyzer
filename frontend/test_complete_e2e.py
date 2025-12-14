"""Complete end-to-end test through frontend UI flow."""
import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

print("=" * 80)
print("COMPLETE END-TO-END TEST - Frontend UI Flow")
print("=" * 80)
print("\nServers running on ALL interfaces (0.0.0.0):")
print(f"  Backend: http://0.0.0.0:8000")
print(f"  Frontend: http://0.0.0.0:8501\n")

results = {
    "backend_health": False,
    "frontend_access": False,
    "pdf_upload": False,
    "topic_extraction": False,
    "chat_search": False,
    "gap_analysis": False,
    "tables_generated": False
}

# Test 1: Backend Health
print("1. Testing Backend Health...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if r.status_code == 200:
        results["backend_health"] = True
        print(f"   [OK] Backend healthy: {r.json()}")
    else:
        print(f"   [FAIL] Status: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 2: Frontend Access
print("\n2. Testing Frontend Access...")
try:
    r = requests.get(f"{FRONTEND_URL}", timeout=5)
    if r.status_code == 200:
        results["frontend_access"] = True
        print(f"   [OK] Frontend accessible")
    else:
        print(f"   [FAIL] Status: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 3: PDF Upload (Full Flow)
print("\n3. Testing PDF Upload and Topic Extraction...")
pdf_path = Path(__file__).parent.parent / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if pdf_path.exists():
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)
        
        if r.status_code == 200:
            result = r.json()
            document_id = result.get("document_id")
            topic_status = result.get("topic_extract_status")
            
            results["pdf_upload"] = True
            results["topic_extraction"] = (topic_status == "completed")
            
            print(f"   [OK] PDF uploaded: {document_id[:8]}...")
            print(f"   [OK] Topic extraction: {topic_status}")
            
            # Test 4: Chat Search
            print("\n4. Testing Chat Search...")
            payload = {
                "message": "Find Data Engineer and Database Administrator jobs from top companies in the last 30 days",
                "document_id": document_id
            }
            r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
            
            if r.status_code == 200:
                result = r.json()
                conversation_id = result.get("conversation_id")
                tool_calls = result.get("tool_calls")
                
                results["chat_search"] = True
                print(f"   [OK] Search completed")
                print(f"   [OK] Conversation ID: {conversation_id[:8]}...")
                print(f"   [OK] Tool called: {tool_calls is not None}")
                
                # Wait for processing
                print("\n   Waiting for search to complete...")
                time.sleep(20)
                
                # Test 5: Gap Analysis
                print("\n5. Testing Gap Analysis...")
                payload = {
                    "message": "Analyze the syllabus topics against the job descriptions and show me the gaps",
                    "conversation_id": conversation_id,
                    "document_id": document_id
                }
                r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
                
                if r.status_code == 200:
                    result = r.json()
                    tables = result.get("tables")
                    
                    results["gap_analysis"] = True
                    if tables:
                        table_a = tables.get("table_a", [])
                        table_b = tables.get("table_b", [])
                        results["tables_generated"] = (len(table_a) > 0 or len(table_b) > 0)
                        
                        print(f"   [OK] Analysis completed")
                        print(f"   [OK] Table A: {len(table_a)} rows")
                        print(f"   [OK] Table B: {len(table_b)} rows")
                        
                        if table_a:
                            sample = table_a[0]
                            print(f"   [OK] Sample Table A: {sample.get('syllabus_topic')} (Score: {sample.get('industry_relevance_score')}%)")
                            refs = sample.get('references', [])
                            if refs:
                                print(f"   [OK] Has {len(refs)} reference URLs")
                        
                        if table_b:
                            sample = table_b[0]
                            print(f"   [OK] Sample Table B: {sample.get('missing_topic')} (Priority: {sample.get('priority')})")
                            refs = sample.get('references', [])
                            if refs:
                                print(f"   [OK] Has {len(refs)} reference URLs")
                    else:
                        print(f"   [WARN] No tables in response")
                else:
                    print(f"   [FAIL] Analysis failed: {r.status_code}")
            else:
                print(f"   [FAIL] Search failed: {r.status_code}")
        else:
            print(f"   [FAIL] PDF upload failed: {r.status_code}")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   [SKIP] PDF not found")

# Final Summary
print("\n" + "=" * 80)
print("FINAL TEST SUMMARY")
print("=" * 80)
for test, passed in results.items():
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} {test.replace('_', ' ').title()}")
print("=" * 80)

all_passed = all(results.values())
if all_passed:
    print("\n[SUCCESS] All tests passed! System is fully operational.")
else:
    print("\n[WARNING] Some tests failed. Check logs above.")
    
print(f"\nAccess the application:")
print(f"  Frontend: http://localhost:8501")
print(f"  Backend: http://localhost:8000")
print(f"  Network: http://192.168.10.150:8501 (frontend)")
print(f"  Network: http://192.168.10.150:8000 (backend)")


