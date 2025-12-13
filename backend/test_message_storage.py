"""Test direct message storage."""
from app.db.session import SessionLocal
from app.db.repositories.chat_message_repo import create_chat_message, get_conversation_messages
from app.db.repositories.conversation_repo import get_or_create_conversation

db = SessionLocal()

try:
    # Create a test conversation
    conv = get_or_create_conversation(db, None)
    conv_id = conv.conversation_id
    print(f"Created conversation: {conv_id[:8]}...")
    
    # Try to create messages
    print("\nCreating test messages...")
    
    msg1 = create_chat_message(db, conv_id, "user", "Test message 1")
    print(f"Created message 1: {msg1.id} - {msg1.content[:30]}...")
    
    msg2 = create_chat_message(db, conv_id, "assistant", "Test response 1")
    print(f"Created message 2: {msg2.id} - {msg2.content[:30]}...")
    
    # Verify they're stored
    messages = get_conversation_messages(db, conv_id)
    print(f"\nRetrieved {len(messages)} messages from database")
    
    for msg in messages:
        print(f"  [{msg.role}] {msg.content}")
    
    if len(messages) == 2:
        print("\n[OK] Messages stored and retrieved successfully!")
    else:
        print(f"\n[FAIL] Expected 2 messages, got {len(messages)}")
        
except Exception as e:
    print(f"\n[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()



