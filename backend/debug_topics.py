"""Debug script to check topic storage."""
from app.db.session import SessionLocal
from app.db.repositories.job_topic_repo import get_topics_by_conversation
from app.db.repositories.job_source_repo import get_sources_by_conversation
from app.db.repositories.syllabus_topic_repo import get_topics_by_document_id

db = SessionLocal()

# Get latest conversation
from app.db.models import Conversation
latest_conv = db.query(Conversation).order_by(Conversation.created_at.desc()).first()

if latest_conv:
    conv_id = latest_conv.conversation_id
    print(f"Latest conversation: {conv_id}")
    
    # Check job sources
    sources = get_sources_by_conversation(db, conv_id)
    print(f"Job sources: {len(sources)}")
    for s in sources[:3]:
        print(f"  - {s.title[:50]}... (text length: {len(s.raw_text or s.snippet)})")
    
    # Check job topics
    topics = get_topics_by_conversation(db, conv_id)
    print(f"\nJob topics: {len(topics)}")
    for t in topics[:10]:
        print(f"  - {t.normalized_topic} (raw: {t.raw_topic})")
    
    # Check syllabus topics
    if latest_conv.documents:
        doc_id = latest_conv.documents[0].document_id
        syllabus_topics = get_topics_by_document_id(db, doc_id)
        print(f"\nSyllabus topics: {len(syllabus_topics)}")
        for t in syllabus_topics[:5]:
            print(f"  - {t.topic_name}")
else:
    print("No conversations found")

db.close()


