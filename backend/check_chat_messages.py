"""Check if chat messages are being stored."""
from app.db.session import SessionLocal
from app.db.models import ChatMessage, Conversation
from sqlalchemy import inspect

db = SessionLocal()

try:
    # Check if table exists
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    
    print("Database Tables:")
    for table in tables:
        print(f"  - {table}")
    
    print(f"\nChatMessage table exists: {'chat_messages' in tables}")
    
    # Count messages
    if 'chat_messages' in tables:
        count = db.query(ChatMessage).count()
        print(f"Total chat messages in DB: {count}")
        
        # Get recent messages
        recent = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(5).all()
        print(f"\nRecent messages ({len(recent)}):")
        for msg in recent:
            print(f"  [{msg.role}] {msg.content[:50]}... (conv: {msg.conversation_id[:8]}...)")
    else:
        print("\n[ERROR] chat_messages table does not exist!")
        print("The database needs to be updated to include the new ChatMessage model.")
        
    # Check conversations
    conv_count = db.query(Conversation).count()
    print(f"\nTotal conversations: {conv_count}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()



