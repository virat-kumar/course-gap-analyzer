# Syllabus vs Industry Gap Analyzer - Project Plan

## Overview
A production-ready backend system that allows users to upload syllabus PDFs, extract topics, search the web for job descriptions based on user constraints, verify collected job data, store evidence in SQLite, and analyze syllabus vs. industry evidence to produce two fixed-schema tables.

## Core Functionality

### Table A: Topics in syllabus that are still viable in industry
- `syllabus_topic`: Topic name from syllabus
- `industry_relevance_score`: 0-100 score
- `evidence_job_count`: Number of jobs mentioning this topic
- `example_industry_phrasing`: How industry phrases this topic
- `notes`: Additional notes
- `references`: List of URLs (REAL URLs only, no hallucination)

### Table B: Missing / emerging topics in industry to add to syllabus
- `missing_topic`: Topic found in jobs but not in syllabus
- `frequency_in_jobs`: Count of jobs mentioning this
- `priority`: High/Medium/Low
- `suggested_syllabus_insertion`: Where/how to add to syllabus
- `rationale`: Why this topic is important
- `references`: List of URLs (REAL URLs only, no hallucination)

---

## Tech Stack (Non-Negotiable)

- **Framework**: FastAPI
- **LLM Framework**: LangChain (tools + agents)
- **Database**: SQLite with SQLAlchemy ORM
- **Data Validation**: Pydantic (strict schemas for tool outputs, verifier outputs)
- **PDF Processing**: PDFPlumber
- **Web Scraping**: BeautifulSoup4
- **Web Search**: Tavily API (via LangChain)
- **LLM Provider**: Azure OpenAI (gpt-4o)
- **Frontend**: Streamlit
- **Environment**: Conda (course-gap-analyzer)

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   ├── routes_pdf.py          # POST /pdf route
│   │   ├── routes_search.py       # POST /search route
│   │   ├── routes_analyze.py      # POST /analyze route
│   │   └── routes_chat.py         # POST /chat route
│   ├── core/
│   │   └── config.py              # Settings (Pydantic-settings)
│   ├── db/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── session.py             # Database session management
│   │   └── repositories/
│   │       ├── conversation_repo.py
│   │       ├── document_repo.py
│   │       ├── syllabus_topic_repo.py
│   │       ├── job_source_repo.py
│   │       ├── job_topic_repo.py
│   │       └── analysis_repo.py
│   ├── schemas/
│   │   ├── pdf.py                 # PDF upload schemas
│   │   ├── search.py              # Search request/response schemas
│   │   ├── verifier.py            # Verifier output schema
│   │   ├── analyze.py             # Analysis request/response schemas
│   │   └── chat.py                # Chat request/response schemas
│   ├── services/
│   │   ├── pdf_service.py         # PDF processing + topic extraction
│   │   ├── search_service.py      # Constraint parsing + web search + verification
│   │   ├── analyze_service.py     # Table generation logic
│   │   └── chat_service.py        # Chat with tool-using agent
│   ├── agents/
│   │   ├── search_agent.py        # LangChain agent for web search
│   │   └── verify_agent.py        # LangChain agent for verification
│   ├── tools/
│   │   ├── pdf_extract_tool.py    # PDF text extraction
│   │   ├── web_search_tool.py     # Tavily search wrapper
│   │   └── fetch_tool.py          # Web page fetching + parsing
│   └── utils/
│       ├── security.py            # Prompt injection guardrails
│       └── text.py                # Topic normalization utilities
├── prompts/
│   └── prompts.py                 # ALL LLM prompts as named constants
├── test_data/
│   └── Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf
├── .env                           # Environment variables
├── requirements.txt
└── test_*.py                      # Test scripts

frontend/
├── app.py                         # Streamlit application
├── requirements.txt
└── start_frontend.bat             # Startup script
```

---

## API Routes Specification

### 1. POST /pdf
**Input**: PDF file (multipart/form-data)
**Output**: 
```json
{
  "document_id": "uuid",
  "extracted_text_preview": "first 500 chars",
  "topic_extract_status": "completed" | "failed"
}
```

**Behavior**:
1. Extract text from PDF using PDFPlumber
2. Store document in `documents` table
3. Run topic extraction pipeline (LLM)
4. Store topics in `syllabus_topics` table
5. Return preview + status

---

### 2. POST /search
**Input**:
```json
{
  "conversation_id": "uuid (optional)",
  "instruction": "string - user's search instruction"
}
```

**Output**:
```json
{
  "conversation_id": "uuid",
  "parsed_constraints": {
    "time_window": "string",
    "role_keywords": ["list"],
    "location": "string",
    "company_tier": "top_companies" | "any",
    "company_allowlist": ["list"],
    "seniority": "string",
    "sources_preference": "string"
  },
  "verified": true | false,
  "results_count": 0,
  "sources_sample": [{"url": "...", "title": "..."}]
}
```

**Behavior**:
1. Parse user instruction → structured constraints (LLM)
2. Web search using constraints (Tavily)
3. Fetch pages/snippets (fetch tool)
4. Extract job topics/skills (LLM)
5. Verifier agent validates evidence
6. Retry if verification fails (up to max_retries)
7. Store verified evidence + sources in database
8. Return parsed constraints + verification status

---

### 3. POST /analyze
**Input**:
```json
{
  "conversation_id": "uuid",
  "document_id": "uuid"
}
```

**Output**:
```json
{
  "table_a": [
    {
      "syllabus_topic": "string",
      "industry_relevance_score": 0-100,
      "evidence_job_count": 0,
      "example_industry_phrasing": "string",
      "notes": "string",
      "references": ["url1", "url2"]
    }
  ],
  "table_b": [
    {
      "missing_topic": "string",
      "frequency_in_jobs": 0,
      "priority": "High" | "Medium" | "Low",
      "suggested_syllabus_insertion": "string",
      "rationale": "string",
      "references": ["url1", "url2"]
    }
  ],
  "analysis_metadata": {
    "analysis_run_id": "uuid",
    "created_at": "timestamp"
  }
}
```

**Behavior**:
1. Load syllabus topics (by document_id)
2. Load verified job topics (by conversation_id)
3. Normalize taxonomy (lowercase, lemmatize, synonyms, dedupe)
4. Compute matches/gaps using LLM
5. Produce tables with references (REAL URLs only)
6. Store analysis outputs in database
7. Return tables + metadata

---

### 4. POST /chat
**Input**:
```json
{
  "conversation_id": "uuid (optional)",
  "message": "string",
  "document_id": "uuid (optional)"
}
```

**Output**:
```json
{
  "response": "assistant response text",
  "conversation_id": "uuid",
  "tool_calls": [{"tool": "search", "status": "completed"}] (optional),
  "tables": { "table_a": [...], "table_b": [...] } (optional)
}
```

**Behavior**:
- Tool-using agent (LangChain)
- Can call internal services (`/search`, `/analyze`) when needed
- Multi-turn conversation support
- Returns tables when analysis is performed

---

## Database Schema (SQLite)

### Tables

1. **conversations**
   - `conversation_id` (String, PK)
   - `created_at` (DateTime)
   - `user_instruction_last` (Text)
   - `parsed_constraints_json` (TEXT/JSON)
   - `status` (String)

2. **documents**
   - `document_id` (String, PK)
   - `conversation_id` (String, FK)
   - `filename` (String)
   - `raw_text` (Text)
   - `created_at` (DateTime)
   - `extraction_method` (String)
   - `ocr_used` (Boolean)

3. **syllabus_topics**
   - `id` (String, PK)
   - `document_id` (String, FK)
   - `topic_name` (String)
   - `module` (String)
   - `keywords_json` (TEXT/JSON)
   - `confidence` (Float)

4. **job_sources**
   - `id` (String, PK)
   - `conversation_id` (String, FK)
   - `url` (String, unique)
   - `source_site` (String)
   - `title` (String)
   - `company` (String)
   - `role` (String)
   - `date_posted` (DateTime)
   - `fetched_at` (DateTime)
   - `snippet` (Text)
   - `raw_text` (Text)
   - `access_status` (String)
   - `content_hash` (String, unique) - for deduplication

5. **job_topics**
   - `id` (String, PK)
   - `job_source_id` (String, FK)
   - `conversation_id` (String, FK)
   - `normalized_topic` (String)
   - `raw_topic` (String)
   - `frequency_weight` (Float)
   - `confidence` (Float)

6. **analysis_runs**
   - `id` (String, PK)
   - `conversation_id` (String, FK)
   - `document_id` (String, FK)
   - `created_at` (DateTime)
   - `model_version` (String)
   - `prompt_version` (String)
   - `tool_versions` (TEXT/JSON)

7. **analysis_table_a_rows**
   - `id` (String, PK)
   - `analysis_run_id` (String, FK)
   - `syllabus_topic` (String)
   - `industry_relevance_score` (Integer, 0-100)
   - `evidence_job_count` (Integer)
   - `example_industry_phrasing` (Text)
   - `notes` (Text)
   - `references_json` (TEXT/JSON)

8. **analysis_table_b_rows**
   - `id` (String, PK)
   - `analysis_run_id` (String, FK)
   - `missing_topic` (String)
   - `frequency_in_jobs` (Integer)
   - `priority` (String)
   - `suggested_syllabus_insertion` (Text)
   - `rationale` (Text)
   - `references_json` (TEXT/JSON)

**Traceability**: All tables linked via `conversation_id` and `document_id`.

---

## Key Design Constraints

### 1. Constraint Parsing
Parse user instruction into structured object:
- `time_window`: "last 30 days", "last 6 months", etc.
- `role_keywords`: ["Data Engineer", "MLOps"]
- `location`: "US", "Remote", "New York"
- `company_tier`: "top_companies" | "any"
- `company_allowlist`: ["Google", "Microsoft"]
- `seniority`: "entry", "mid", "senior"
- `sources_preference`: "job_boards", "company_sites", "all"

**Output**: Strict JSON from LLM, validated with Pydantic.

---

### 2. "Top Companies" Rule
- **Objective rule**: Config-based allowlist in `config.py`
- Default list: Google, Microsoft, Amazon, Apple, Meta, etc.
- Verifier agent uses same rule
- Documented in code comments

---

### 3. Evidence Collection & Web Search
- Use LangChain Tavily search tool
- Fetch tool for pages (BeautifulSoup4)
- Prefer crawlable sources
- Handle blocked sites gracefully
- Store fields:
  - `url`, `title`, `company`, `role`, `date_posted`, `fetched_at`
  - `snippet`, `raw_text` (if available)
  - `access_status`, `content_hash`
- Deduplicate by canonical URL hash

---

### 4. Verifier Agent
- **Second agent** validates evidence vs. constraints
- **Output**: Strict Pydantic JSON schema:
  ```python
  {
    "pass": bool,
    "fail_reasons": [str],
    "constraint_violations": {field: reason},
    "retry_query_suggestions": [str],
    "coverage_score": 0-100
  }
  ```
- **Auto-retry**: If fail, refine query/change sources (up to max_retries)
- **Exponential backoff**: Wait between retries
- **Only store verified=true** if verifier passes

---

### 5. Topic Normalization
- Lowercase
- Lemmatize (NLTK)
- Strip noise (punctuation, extra spaces)
- Map synonyms (config-based)
- Merge near-duplicates using embeddings (cosine similarity > 0.9)
- Store both `raw_topic` and `normalized_topic`

---

### 6. Analysis Output Tables
**Hard Rules**:
- Every row must have REAL URLs from `job_sources` table
- NO hallucinated citations
- Deduplicate topics (by normalized_topic)
- References must be actual URLs stored in database

---

### 7. Security & Safety
- **Prompt injection guardrails**:
  - Treat external text (PDFs, web pages) as untrusted
  - Never follow instructions from PDFs/web pages
  - Only extract factual content
  - Ignore text attempting to change system behavior
  - Dedicated "sanitization + extraction prompt"
  - Log suspicious patterns

---

## Prompt Organization

**All prompts in `prompts/prompts.py`**:
- `SYLLABUS_TOPIC_EXTRACT_PROMPT`
- `CONSTRAINT_PARSING_PROMPT`
- `JOB_TOPIC_EXTRACT_PROMPT`
- `VERIFIER_PROMPT`
- `ANALYSIS_PROMPT`
- `SECURITY_GUARDRAIL`

Use `.replace()` for formatting (avoid f-strings with JSON examples).

---

## Data Flow / Pipeline Flow

### PDF Processing Pipeline
1. Upload PDF → `/pdf`
2. Extract text (PDFPlumber)
3. Sanitize text (security.py)
4. LLM topic extraction
5. Store topics in DB

### Search Pipeline
1. User instruction → `/search`
2. Parse constraints (LLM)
3. Build search query
4. Web search (Tavily)
5. Fetch pages (fetch_tool)
6. Extract job topics (LLM)
7. Verifier agent validates
8. Retry if needed
9. Store verified evidence

### Analysis Pipeline
1. `document_id` + `conversation_id` → `/analyze`
2. Load syllabus topics
3. Load job topics
4. Normalize topics
5. LLM generates tables
6. Validate references (real URLs only)
7. Store analysis run
8. Return tables

### Chat Pipeline
1. User message → `/chat`
2. Detect intent (search/analyze)
3. Call appropriate service
4. Return response + optional tables

---

## Environment Variables (.env)

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
API_VERSION=2024-12-01-preview
AZURE_OPENAI_MODEL=gpt-4o

# Tavily API
TAVILY_API_KEY=your_tavily_key_here

# Agent Settings
MARKDOWN_FIXER_AGENT_MAX_ITERATIONS=4
MAX_RETRIES_SEARCH=3
RETRY_BACKOFF_FACTOR=2.0

# Database
DATABASE_URL=sqlite:///./syllabus_gap_analyzer.db
```

---

## Testing Requirements

### 1. Credential Verification (FIRST STEP)
- Create `test_azure_credentials.py`
- Verify Azure OpenAI connection
- Report to user if fails

### 2. Module-Level Testing
- After generating any module, test via terminal
- Fix errors immediately
- Verify basic functionality

### 3. End-to-End Integration Testing
- Start FastAPI server
- Upload `Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf` via `/pdf`
- Test full chat flow (`/search` then `/analyze`)
- Monitor logs
- Fix errors
- Verify tables with real URLs

---

## Server Configuration

### Backend (FastAPI)
- Host: `0.0.0.0` (all interfaces)
- Port: `8000`
- Auto-reload: Enabled
- Log level: `info`

### Frontend (Streamlit)
- Host: `0.0.0.0` (all interfaces)
- Port: `8501`

### Firewall Rules
- Port 8000: FastAPI Backend
- Port 8501: Streamlit Frontend

---

## Implementation Status

✅ Backend structure created
✅ Database models implemented
✅ API routes implemented
✅ Services implemented
✅ Agents implemented
✅ Tools implemented
✅ Security guardrails implemented
✅ Frontend Streamlit app created
✅ Testing scripts created
✅ Firewall rules configured
✅ Documentation created

---

## Next Steps / Future Enhancements

- Add authentication/authorization
- Support multiple LLM providers
- Add caching layer
- Implement rate limiting
- Add monitoring/logging (e.g., Prometheus)
- Export analysis results (PDF, Excel)
- Support multiple syllabus formats
- Advanced topic clustering
- Industry trend analysis over time

---

## Notes

- All UUIDs stored as String in SQLite (SQLite limitation)
- JSON fields stored as TEXT in SQLite
- Topic normalization uses embeddings for near-duplicate detection
- Verifier agent uses same "top companies" rule as search
- All prompts centralized in `prompts/prompts.py`
- Security guardrails prevent prompt injection
- References in tables are always real URLs from database

---

**Last Updated**: 2025-01-XX
**Version**: 1.0

