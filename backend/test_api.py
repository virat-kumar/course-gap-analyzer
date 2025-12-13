"""Simple API test script."""
import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

print("Testing API endpoints...\n")

# Test 1: Health check
print("1. Health check...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

# Test 2: PDF upload
print("2. PDF upload...")
pdf_path = Path(__file__).parent / "test_data" / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if pdf_path.exists():
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            r = requests.post(f"{BASE_URL}/pdf", files=files, timeout=60)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"   Document ID: {result.get('document_id')}")
            print(f"   Topic extract status: {result.get('topic_extract_status')}")
            document_id = result.get('document_id')
        else:
            print(f"   ERROR: {r.text}")
            document_id = None
    except Exception as e:
        print(f"   ERROR: {e}")
        document_id = None
else:
    print(f"   ERROR: PDF file not found at {pdf_path}")
    document_id = None

print()

# Test 3: Chat search
if document_id:
    print("3. Chat - Search request...")
    try:
        payload = {
            "message": "Find Data Engineer jobs from top companies in the last 30 days",
            "document_id": document_id
        }
        r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"   Response: {result.get('response', '')[:100]}...")
            conversation_id = result.get('conversation_id')
        else:
            print(f"   ERROR: {r.text[:200]}")
            conversation_id = None
    except Exception as e:
        print(f"   ERROR: {e}")
        conversation_id = None
else:
    conversation_id = None
    print("3. Skipping chat test (no document_id)\n")

print()
print("Test summary:")
print(f"  - Server: {'OK' if r.status_code == 200 else 'FAILED'}")
print(f"  - PDF upload: {'OK' if document_id else 'FAILED'}")
print(f"  - Chat search: {'OK' if conversation_id else 'FAILED'}")


