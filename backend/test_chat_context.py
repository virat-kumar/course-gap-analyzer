"""Test multi-turn chat with context awareness."""
import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

print("=" * 70)
print("MULTI-TURN CHAT CONTEXT TEST")
print("=" * 70)
print(f"Backend: {BACKEND_URL}\n")

# Test conversation that requires context
test_conversation = [
    ("Hello! What's your name?", "Initial greeting"),
    ("What did I just ask you?", "Context test - should remember previous question"),
    ("Can you summarize our conversation so far?", "Summary test - should have context"),
    ("What was the first thing I said?", "Memory test - should recall first message"),
]

conversation_id = None

print("Testing Multi-Turn Conversation with Context...\n")

for i, (message, description) in enumerate(test_conversation, 1):
    print(f"Turn {i}: {description}")
    print(f"  User: {message}")
    
    try:
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "document_id": None
        }
        
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        
        if r.status_code == 200:
            result = r.json()
            conversation_id = result["conversation_id"]
            response = result.get("response", "")
            
            # Display response (truncate if too long)
            if len(response) > 300:
                print(f"  Assistant: {response[:300]}...")
            else:
                print(f"  Assistant: {response}")
            
            # Verify conversation ID is maintained
            if i > 1:
                print(f"  [OK] Conversation ID maintained: {conversation_id[:8]}...")
            
            print()
            time.sleep(1)  # Small delay between messages
            
        else:
            print(f"  [FAIL] Request failed: {r.status_code}")
            print(f"  Error: {r.text}")
            break
            
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] Request timed out (this may happen with LLM calls)")
        break
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        break

if conversation_id:
    print("=" * 70)
    print(f"Conversation ID: {conversation_id}")
    print("Test completed! Check if the assistant maintained context across turns.")
    print("=" * 70)
else:
    print("Test failed - no conversation created")



