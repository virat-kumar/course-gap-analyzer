"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.session import Base


class Conversation(Base):
    """Conversation table - tracks user sessions."""
    __tablename__ = "conversations"
    
    conversation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_instruction_last = Column(Text)
    parsed_constraints_json = Column(JSON)
    status = Column(String(50))  # e.g., "active", "completed", "failed"
    
    # Relationships
    job_sources = relationship("JobSource", back_populates="conversation", cascade="all, delete-orphan")
    job_topics = relationship("JobTopic", back_populates="conversation", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="conversation", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    __table_args__ = (
        Index("idx_conversation_created", "created_at"),
    )


class ChatMessage(Base):
    """Chat messages for multi-turn conversations."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = Column(JSON)  # Store tool calls, tables, etc.
    
    # Relationships
    conversation = relationship("Conversation", back_populates="chat_messages")
    
    __table_args__ = (
        Index("idx_chat_conversation", "conversation_id"),
        Index("idx_chat_created", "created_at"),
    )


class Document(Base):
    """Documents table - stores uploaded PDFs."""
    __tablename__ = "documents"
    
    document_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extraction_method = Column(String(50))  # e.g., "pypdf2", "pdfplumber", "ocr"
    ocr_used = Column(Boolean, default=False)
    
    # Relationships
    syllabus_topics = relationship("SyllabusTopic", back_populates="document", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_document_created", "created_at"),
    )


class SyllabusTopic(Base):
    """Syllabus topics extracted from PDF."""
    __tablename__ = "syllabus_topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    topic_name = Column(String(255), nullable=False)
    module = Column(String(100))  # e.g., "Week 1", "Module 2"
    keywords_json = Column(JSON)  # List of related keywords
    confidence = Column(Float)  # Extraction confidence score
    
    # Relationships
    document = relationship("Document", back_populates="syllabus_topics")
    
    __table_args__ = (
        Index("idx_syllabus_document", "document_id"),
        Index("idx_syllabus_topic", "topic_name"),
    )


class JobSource(Base):
    """Job sources - individual job postings found via web search."""
    __tablename__ = "job_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    source_site = Column(String(100))  # e.g., "greenhouse", "lever", "company_career_page"
    title = Column(String(255))
    company = Column(String(255))
    role = Column(String(255))
    date_posted = Column(DateTime)  # If available from source
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    snippet = Column(Text)  # Search snippet or summary
    raw_text = Column(Text)  # Full page text if available
    access_status = Column(String(50))  # e.g., "success", "blocked", "timeout", "error"
    content_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Relationships
    conversation = relationship("Conversation", back_populates="job_sources")
    job_topics = relationship("JobTopic", back_populates="job_source", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_job_source_conversation", "conversation_id"),
        Index("idx_job_source_hash", "content_hash"),
        Index("idx_job_source_company", "company"),
        Index("idx_job_source_fetched", "fetched_at"),
    )


class JobTopic(Base):
    """Topics/skills extracted from job descriptions."""
    __tablename__ = "job_topics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_source_id = Column(Integer, ForeignKey("job_sources.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=False)
    normalized_topic = Column(String(255), nullable=False)  # Normalized topic name
    raw_topic = Column(String(255))  # Original topic as extracted
    frequency_weight = Column(Float, default=1.0)  # Weight for frequency analysis
    confidence = Column(Float)  # Extraction confidence
    
    # Relationships
    job_source = relationship("JobSource", back_populates="job_topics")
    conversation = relationship("Conversation", back_populates="job_topics")
    
    __table_args__ = (
        Index("idx_job_topic_source", "job_source_id"),
        Index("idx_job_topic_conversation", "conversation_id"),
        Index("idx_job_topic_normalized", "normalized_topic"),
    )


class AnalysisRun(Base):
    """Analysis runs - tracks each gap analysis execution."""
    __tablename__ = "analysis_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.conversation_id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_version = Column(String(50))  # e.g., "gpt-4o"
    prompt_version = Column(String(50))  # Prompt version identifier
    tool_versions = Column(JSON)  # Versions of tools used
    notes = Column(Text)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="analysis_runs")
    document = relationship("Document", back_populates="analysis_runs")
    table_a_rows = relationship("AnalysisTableARow", back_populates="analysis_run", cascade="all, delete-orphan")
    table_b_rows = relationship("AnalysisTableBRow", back_populates="analysis_run", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_analysis_conversation", "conversation_id"),
        Index("idx_analysis_document", "document_id"),
        Index("idx_analysis_created", "created_at"),
    )


class AnalysisTableARow(Base):
    """Table A: Syllabus topics still viable in industry."""
    __tablename__ = "analysis_table_a_rows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    syllabus_topic = Column(String(255), nullable=False)
    industry_relevance_score = Column(Integer)  # 0-100
    evidence_job_count = Column(Integer)  # Number of jobs mentioning this
    example_industry_phrasing = Column(Text)  # 1-2 short phrases
    notes = Column(Text)
    references_json = Column(JSON)  # List of URLs from job_sources
    
    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="table_a_rows")
    
    __table_args__ = (
        Index("idx_table_a_run", "analysis_run_id"),
        Index("idx_table_a_topic", "syllabus_topic"),
    )


class AnalysisTableBRow(Base):
    """Table B: Missing/emerging topics to add to syllabus."""
    __tablename__ = "analysis_table_b_rows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    missing_topic = Column(String(255), nullable=False)
    frequency_in_jobs = Column(Integer)  # Count of jobs mentioning this
    priority = Column(String(20))  # "High", "Medium", "Low"
    suggested_syllabus_insertion = Column(String(255))  # Where to add (e.g., "Week 3", "Module 2")
    rationale = Column(Text)
    references_json = Column(JSON)  # List of URLs from job_sources
    
    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="table_b_rows")
    
    __table_args__ = (
        Index("idx_table_b_run", "analysis_run_id"),
        Index("idx_table_b_topic", "missing_topic"),
        Index("idx_table_b_priority", "priority"),
    )

