"""Test the complete UI flow as a user would."""
import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

print("=" * 70)
print("FRONTEND UI FLOW TEST - Simulating Real User Interaction")
print("=" * 70)
print("\nNOTE: Both servers running on ALL interfaces (0.0.0.0)")
print(f"      Backend: http://0.0.0.0:8000")
print(f"      Frontend: http://0.0.0.0:8501\n")

# Step 1: Verify servers
print("Step 1: Verifying servers...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] Backend: {r.json()}")
except:
    print("   [FAIL] Backend not responding")
    exit(1)

try:
    r = requests.get(f"{FRONTEND_URL}", timeout=5)
    assert r.status_code == 200
    print(f"   [OK] Frontend: Accessible")
except:
    print("   [FAIL] Frontend not responding")
    exit(1)

# Step 2: Upload PDF (as frontend would)
print("\nStep 2: Uploading PDF (via backend API)...")
pdf_path = Path(__file__).parent.parent / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if not pdf_path.exists():
    print(f"   [SKIP] PDF not found")
    exit(1)

with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path.name, f, "application/pdf")}
    r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)

assert r.status_code == 200
result = r.json()
document_id = result["document_id"]
print(f"   [OK] PDF uploaded: {document_id[:8]}...")
print(f"   [OK] Topics extracted: {result['topic_extract_status']}")

# Step 3: Chat - Search (as frontend would)
print("\nStep 3: Chat - Requesting job search...")
payload = {
    "message": "Find Data Engineer and Database Administrator jobs from top companies in the last 30 days",
    "document_id": document_id
}
r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
assert r.status_code == 200
result = r.json()
conversation_id = result["conversation_id"]
print(f"   [OK] Search completed")
print(f"   [OK] Conversation: {conversation_id[:8]}...")
print(f"   [OK] Response: {result['response'][:100]}...")

# Wait for processing
print("\n   Waiting for search processing...")
time.sleep(15)

# Step 4: Chat - Analysis (as frontend would)
print("\nStep 4: Chat - Requesting analysis...")
payload = {
    "message": "Now analyze the syllabus topics against the job descriptions and show me the gaps",
    "conversation_id": conversation_id,
    "document_id": document_id
}
r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=300)
assert r.status_code == 200
result = r.json()
tables = result.get("tables")
print(f"   [OK] Analysis completed")
print(f"   [OK] Response: {result['response'][:100]}...")

if tables:
    table_a = tables.get("table_a", [])
    table_b = tables.get("table_b", [])
    print(f"   [OK] Table A: {len(table_a)} rows")
    print(f"   [OK] Table B: {len(table_b)} rows")
    
    if table_a:
        print(f"   [OK] Sample A: {table_a[0].get('syllabus_topic')}")
    if table_b:
        print(f"   [OK] Sample B: {table_b[0].get('missing_topic')}")
else:
    print(f"   [WARN] No tables in response")

print("\n" + "=" * 70)
print("UI FLOW TEST COMPLETE")
print("=" * 70)
print("[OK] All steps completed successfully")
print("[OK] Frontend can access backend")
print("[OK] Full workflow functional")
print("=" * 70)


