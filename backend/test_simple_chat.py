"""Simple test to verify message storage."""
import requests
import time
from app.db.session import SessionLocal
from app.db.repositories.chat_message_repo import get_conversation_messages

BACKEND_URL = "http://localhost:8000"

print("Simple Chat Test with Database Verification")
print("=" * 50)

# Send a single message
print("\n1. Sending message to chat endpoint...")
payload = {
    "message": "Hello, this is a test message",
    "conversation_id": None,
    "document_id": None
}

r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
if r.status_code == 200:
    result = r.json()
    conv_id = result["conversation_id"]
    print(f"   [OK] Response received")
    print(f"   Conversation ID: {conv_id}")
    print(f"   Response: {result.get('response', '')[:100]}...")
    
    # Wait a moment for DB to update
    time.sleep(2)
    
    # Check database
    print("\n2. Checking database...")
    db = SessionLocal()
    try:
        messages = get_conversation_messages(db, conv_id)
        print(f"   Found {len(messages)} messages in database")
        
        if len(messages) > 0:
            print("\n   Messages:")
            for msg in messages:
                print(f"     [{msg.role}] {msg.content[:50]}...")
        else:
            print("   [FAIL] No messages found!")
            print("   Checking all messages in database...")
            from app.db.models import ChatMessage
            all_msgs = db.query(ChatMessage).limit(10).all()
            print(f"   Total messages in DB: {len(all_msgs)}")
            if len(all_msgs) > 0:
                print("   Recent messages:")
                for msg in all_msgs:
                    print(f"     [{msg.role}] Conv: {msg.conversation_id[:8]}... - {msg.content[:30]}...")
    finally:
        db.close()
else:
    print(f"   [FAIL] Request failed: {r.status_code}")
    print(f"   Error: {r.text}")



