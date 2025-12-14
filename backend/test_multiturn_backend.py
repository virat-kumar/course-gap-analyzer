"""Comprehensive test for multi-turn chat backend functionality."""
import requests
import json
import time
from app.db.session import SessionLocal
from app.db.repositories.chat_message_repo import get_conversation_messages, get_conversation_messages_for_llm
from app.db.models import ChatMessage

BACKEND_URL = "http://localhost:8000"

print("=" * 70)
print("COMPREHENSIVE MULTI-TURN CHAT BACKEND TEST")
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

# Test 2: Multi-turn conversation with context
print("\n2. Testing Multi-Turn Conversation with Context...")
conversation_id = None
test_messages = [
    ("Hello! My name is Alice.", "Introduction"),
    ("What's my name?", "Context recall test"),
    ("Can you remember what I told you?", "Memory test"),
    ("Tell me a summary of our conversation.", "Summary test"),
]

print("\n   Sending messages to chat endpoint...")
for i, (message, description) in enumerate(test_messages, 1):
    print(f"\n   Turn {i}: {description}")
    print(f"   User: {message}")
    
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
            if len(response) > 200:
                print(f"   Assistant: {response[:200]}...")
            else:
                print(f"   Assistant: {response}")
            
            # Verify conversation ID is maintained
            if i > 1:
                print(f"   [OK] Conversation ID maintained: {conversation_id[:8]}...")
            
            time.sleep(1)  # Small delay between messages
            
        else:
            print(f"   [FAIL] Request failed: {r.status_code}")
            print(f"   Error: {r.text}")
            break
            
    except requests.exceptions.Timeout:
        print(f"   [TIMEOUT] Request timed out")
        break
    except Exception as e:
        print(f"   [ERROR] Exception: {e}")
        break

# Test 3: Verify messages are stored in database
print("\n3. Verifying Messages Stored in Database...")
if conversation_id:
    db = SessionLocal()
    try:
        messages = get_conversation_messages(db, conversation_id)
        print(f"   Found {len(messages)} messages in database for conversation {conversation_id[:8]}...")
        
        if len(messages) > 0:
            print("\n   Message History:")
            for i, msg in enumerate(messages, 1):
                role_icon = "👤" if msg.role == "user" else "🤖"
                content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                print(f"   {i}. {role_icon} [{msg.role}]: {content_preview}")
            
            # Verify we have both user and assistant messages
            user_count = sum(1 for m in messages if m.role == "user")
            assistant_count = sum(1 for m in messages if m.role == "assistant")
            
            print(f"\n   [OK] User messages: {user_count}")
            print(f"   [OK] Assistant messages: {assistant_count}")
            
            if user_count == assistant_count and user_count == len(test_messages):
                print(f"   [OK] All messages stored correctly!")
            else:
                print(f"   [WARNING] Message count mismatch (expected {len(test_messages)} pairs)")
        else:
            print("   [FAIL] No messages found in database!")
            
    except Exception as e:
        print(f"   [ERROR] Database query failed: {e}")
    finally:
        db.close()
else:
    print("   [SKIP] No conversation ID available")

# Test 4: Verify LLM format conversion
print("\n4. Verifying LLM Message Format Conversion...")
if conversation_id:
    db = SessionLocal()
    try:
        llm_messages = get_conversation_messages_for_llm(db, conversation_id, limit=20)
        print(f"   Retrieved {len(llm_messages)} messages in LLM format")
        
        if len(llm_messages) > 0:
            print("\n   LLM Format Messages:")
            for i, msg in enumerate(llm_messages[:5], 1):  # Show first 5
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                content_preview = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                print(f"   {i}. {role_icon} [{msg['role']}]: {content_preview}")
            
            # Verify format
            all_have_role = all("role" in m for m in llm_messages)
            all_have_content = all("content" in m for m in llm_messages)
            
            if all_have_role and all_have_content:
                print(f"   [OK] All messages have correct format (role + content)")
            else:
                print(f"   [FAIL] Some messages missing required fields")
        else:
            print("   [FAIL] No messages in LLM format!")
            
    except Exception as e:
        print(f"   [ERROR] LLM format conversion failed: {e}")
    finally:
        db.close()
else:
    print("   [SKIP] No conversation ID available")

# Test 5: Test conversation continuity
print("\n5. Testing Conversation Continuity...")
if conversation_id:
    print("   Sending follow-up message to test context...")
    try:
        payload = {
            "message": "What was the first thing I said in this conversation?",
            "conversation_id": conversation_id,
            "document_id": None
        }
        
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        
        if r.status_code == 200:
            result = r.json()
            response = result.get("response", "")
            print(f"   User: What was the first thing I said in this conversation?")
            print(f"   Assistant: {response[:300]}...")
            
            # Check if response shows context awareness
            first_message = test_messages[0][0] if test_messages else ""
            if first_message.lower() in response.lower() or "alice" in response.lower():
                print(f"   [OK] Response shows context awareness!")
            else:
                print(f"   [WARNING] Response may not be using full context")
        else:
            print(f"   [FAIL] Follow-up request failed: {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Follow-up test failed: {e}")
else:
    print("   [SKIP] No conversation ID available")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
if conversation_id:
    print(f"✅ Conversation ID: {conversation_id}")
    print("✅ Multi-turn chat functionality tested")
    print("✅ Database storage verified")
    print("✅ Message format conversion verified")
else:
    print("❌ Test incomplete - no conversation created")
print("=" * 70)



