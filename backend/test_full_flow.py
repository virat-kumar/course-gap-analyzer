"""Full end-to-end test of the complete flow."""
import requests
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("FULL END-TO-END TEST")
print("=" * 60)

# Step 1: Health check
print("\n1. Health check...")
r = requests.get(f"{BASE_URL}/health", timeout=5)
assert r.status_code == 200, f"Health check failed: {r.status_code}"
print(f"   [OK] Server is healthy")

# Step 2: Upload PDF
print("\n2. Uploading PDF...")
pdf_path = Path("test_data/Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf")
assert pdf_path.exists(), f"PDF not found: {pdf_path}"

with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path.name, f, "application/pdf")}
    r = requests.post(f"{BASE_URL}/pdf", files=files, timeout=120)

assert r.status_code == 200, f"PDF upload failed: {r.status_code} - {r.text}"
result = r.json()
document_id = result.get("document_id")
topic_status = result.get("topic_extract_status")
print(f"   [OK] PDF uploaded")
print(f"   Document ID: {document_id}")
print(f"   Topic extraction: {topic_status}")
assert topic_status == "completed", f"Topic extraction failed: {topic_status}"

# Wait a bit for processing
time.sleep(2)

# Step 3: Chat - Search request
print("\n3. Chat - Search for jobs...")
payload = {
    "message": "Find Data Engineer and Database Administrator jobs from top companies in the last 30 days in the US",
    "document_id": document_id
}
r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=300)
assert r.status_code == 200, f"Chat search failed: {r.status_code} - {r.text}"

result = r.json()
conversation_id = result.get("conversation_id")
response_text = result.get("response", "")
tool_calls = result.get("tool_calls")

print(f"   [OK] Chat responded")
print(f"   Conversation ID: {conversation_id}")
print(f"   Response: {response_text[:150]}...")
print(f"   Tool calls: {tool_calls}")

# Check if search was triggered
if tool_calls and any("search" in str(tc).lower() for tc in tool_calls):
    print("   [OK] Search tool was called")
else:
    print("   [WARN] Search tool may not have been called")
    print(f"   Full response: {response_text}")

# Step 4: Chat - Analysis request
print("\n4. Chat - Request analysis...")
if conversation_id:
    payload = {
        "message": "Now analyze the syllabus topics against the job descriptions and show me the gaps",
        "conversation_id": conversation_id,
        "document_id": document_id
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=300)
    
    if r.status_code == 200:
        result = r.json()
        tables = result.get("tables")
        response_text = result.get("response", "")
        
        print(f"   [OK] Analysis completed")
        print(f"   Response: {response_text[:150]}...")
        
        if tables:
            table_a = tables.get("table_a", [])
            table_b = tables.get("table_b", [])
            print(f"   Table A rows: {len(table_a)}")
            print(f"   Table B rows: {len(table_b)}")
            
            if table_a:
                print(f"   Sample Table A row: {table_a[0]}")
            if table_b:
                print(f"   Sample Table B row: {table_b[0]}")
        else:
            print("   [WARN] No tables in response")
    else:
        print(f"   [WARN] Analysis request failed: {r.status_code} - {r.text[:200]}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("[OK] PDF Upload: SUCCESS")
print("[OK] Topic Extraction: SUCCESS")
print("[OK] Chat Search: SUCCESS" if conversation_id else "[WARN] Chat Search: NEEDS CHECK")
print("[OK] Analysis: SUCCESS" if r.status_code == 200 else "[WARN] Analysis: NEEDS CHECK")
print("=" * 60)

