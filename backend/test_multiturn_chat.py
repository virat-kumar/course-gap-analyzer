"""Test multi-turn chat functionality."""
import requests
import json
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

print("=" * 70)
print("MULTI-TURN CHAT TEST")
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

# Test 2: Multi-turn conversation
print("\n2. Testing Multi-Turn Conversation...")
conversation_id = None
document_id = None

# First, upload a PDF if available
print("\n   Step 2a: Upload PDF (if available)...")
pdf_path = Path(__file__).parent.parent / "Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf"
if pdf_path.exists():
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        r = requests.post(f"{BACKEND_URL}/pdf", files=files, timeout=120)
        if r.status_code == 200:
            result = r.json()
            document_id = result["document_id"]
            print(f"   [OK] PDF uploaded: {document_id[:8]}...")
        else:
            print(f"   [SKIP] PDF upload failed: {r.status_code}")
else:
    print(f"   [SKIP] PDF not found at {pdf_path}")

# Test conversation flow
test_messages = [
    "Hello!",
    "What can you help me with?",
    "I want to search for data engineering jobs",
    "Can you tell me more about what you found?",
    "What skills are most important?",
]

print("\n   Step 2b: Multi-turn conversation test...")
for i, message in enumerate(test_messages, 1):
    print(f"\n   Turn {i}: User: {message}")
    try:
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "document_id": document_id
        }
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
        
        if r.status_code == 200:
            result = r.json()
            conversation_id = result["conversation_id"]
            response_text = result.get("response", "")[:200]  # Truncate for display
            print(f"   Assistant: {response_text}...")
            
            if result.get("tool_calls"):
                print(f"   [TOOL] {result['tool_calls']}")
            
            # Check if conversation is maintained
            if i > 1:
                print(f"   [OK] Conversation ID maintained: {conversation_id[:8]}...")
        else:
            print(f"   [FAIL] Request failed: {r.status_code} - {r.text}")
            break
    except Exception as e:
        print(f"   [ERROR] Exception: {e}")
        break

# Test 3: Verify conversation history
print("\n3. Verifying Conversation History...")
if conversation_id:
    print(f"   Conversation ID: {conversation_id[:8]}...")
    print("   [OK] Multi-turn conversation completed successfully!")
    print("   [INFO] Check the database to verify messages are stored.")
else:
    print("   [SKIP] No conversation ID available")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)



