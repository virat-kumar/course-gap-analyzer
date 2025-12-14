"""Test chat LLM functionality."""
import requests
import json

BACKEND_URL = "http://localhost:8000"

print("Testing Chat LLM Functionality")
print("=" * 50)

# Test 1: Health check
print("\n1. Health check...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   [FAIL] {e}")
    exit(1)

# Test 2: Simple chat message
print("\n2. Testing chat with LLM...")
payload = {
    "message": "Hello! Can you help me?",
    "conversation_id": None,
    "document_id": None
}

try:
    r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
    print(f"   Status: {r.status_code}")
    
    if r.status_code == 200:
        result = r.json()
        print(f"   Conversation ID: {result.get('conversation_id', 'N/A')[:8]}...")
        response = result.get('response', '')
        print(f"   Response length: {len(response)} chars")
        print(f"   Response preview: {response[:200]}...")
        
        # Check if it's the fallback response
        if "I can help you:\n1. Search for job descriptions" in response:
            print("   [WARNING] Got fallback response - LLM may have failed")
        else:
            print("   [OK] Got LLM response (not fallback)")
    else:
        print(f"   [FAIL] Status {r.status_code}: {r.text}")
        
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Multi-turn
print("\n3. Testing multi-turn conversation...")
conv_id = None
for i, msg in enumerate(["Hi", "What can you do?", "Tell me more"], 1):
    print(f"\n   Turn {i}: {msg}")
    payload = {
        "message": msg,
        "conversation_id": conv_id,
        "document_id": None
    }
    
    try:
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        if r.status_code == 200:
            result = r.json()
            conv_id = result.get("conversation_id")
            response = result.get("response", "")[:150]
            print(f"   Response: {response}...")
            
            if i > 1:
                print(f"   [OK] Conversation ID maintained: {conv_id[:8] if conv_id else 'N/A'}...")
        else:
            print(f"   [FAIL] Status {r.status_code}")
            break
    except Exception as e:
        print(f"   [ERROR] {e}")
        break

print("\n" + "=" * 50)
print("Test complete!")

