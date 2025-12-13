# 📚 Syllabus Gap Analyzer

A production-ready web application that compares course syllabi against industry job descriptions to identify gaps and viable topics. Upload your syllabus PDF, search for relevant job postings, and get detailed analysis reports showing which topics are still relevant and what's missing from your curriculum.

## 🌟 Features

### Core Functionality

- **📄 PDF Upload & Topic Extraction**: Upload syllabus PDFs and automatically extract educational topics using AI
- **🔍 Intelligent Job Search**: Search for industry job descriptions based on custom constraints (location, company tier, role keywords, etc.)
- **📊 Gap Analysis**: Generate comprehensive analysis reports comparing syllabus topics with industry requirements
- **💬 Chat Interface**: Interact with the system using natural language - upload PDFs, search jobs, and request analysis through conversational interface
- **🔄 Multi-turn Conversations**: Maintain context across multiple interactions with persistent conversation history

### Analysis Output

The system generates two comprehensive tables:

**Table A: Viable Topics**
- Topics from your syllabus that are still relevant in industry
- Industry relevance score (0-100%)
- Evidence from job descriptions
- Example industry phrasing
- Reference URLs to actual job postings

**Table B: Missing Topics**
- Emerging topics found in industry but missing from your syllabus
- Frequency in job postings
- Priority rating (High/Medium/Low)
- Suggested syllabus insertion points
- Rationale for inclusion
- Reference URLs

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework**: FastAPI 0.124.4
- **LLM Framework**: LangChain 1.1.3
- **LLM Provider**: Azure OpenAI (GPT-4o)
- **Database**: SQLite with SQLAlchemy ORM 2.0.45
- **PDF Processing**: PDFPlumber 0.11.8
- **Web Search**: Tavily API (via LangChain)
- **Web Scraping**: BeautifulSoup4 4.14.3
- **Data Validation**: Pydantic 2.12.5

**Frontend:**
- **Framework**: Streamlit
- **Communication**: REST API with requests

**Development:**
- **Environment**: Conda (course-gap-analyzer environment)
- **Testing**: pytest 8.3.4

### Project Structure

```
course-gap-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── api/                       # API route handlers
│   │   │   ├── routes_pdf.py          # PDF upload endpoint
│   │   │   ├── routes_search.py       # Job search endpoint
│   │   │   ├── routes_analyze.py      # Gap analysis endpoint
│   │   │   └── routes_chat.py         # Chat interface endpoint
│   │   ├── core/
│   │   │   └── config.py              # Configuration management
│   │   ├── db/
│   │   │   ├── models.py              # SQLAlchemy database models
│   │   │   ├── session.py             # Database session management
│   │   │   └── repositories/          # Data access layer
│   │   ├── services/                  # Business logic
│   │   │   ├── pdf_service.py         # PDF processing service
│   │   │   ├── search_service.py      # Job search service
│   │   │   ├── analyze_service.py     # Gap analysis service
│   │   │   └── chat_service.py        # Chat conversation service
│   │   ├── tools/                     # LangChain tools
│   │   │   ├── pdf_extract_tool.py    # PDF text extraction
│   │   │   ├── web_search_tool.py     # Tavily web search
│   │   │   └── fetch_tool.py          # Web page fetching
│   │   ├── agents/                    # LangChain agents
│   │   │   └── verify_agent.py        # Job verification agent
│   │   ├── utils/                     # Utility functions
│   │   │   ├── security.py            # Security sanitization
│   │   │   └── text.py                # Text processing
│   │   └── schemas/                   # Pydantic schemas
│   ├── prompts/
│   │   └── prompts.py                 # All LLM prompts
│   ├── test_data/
│   │   └── Fall_2025_Syllabus_V1.0_BUAN6320.005.pdf
│   ├── requirements.txt               # Python dependencies
│   ├── start_backend.bat             # Backend startup script
│   └── .env                          # Environment variables (not in git)
│
├── frontend/
│   ├── app.py                        # Streamlit application
│   ├── requirements.txt              # Frontend dependencies
│   └── start_frontend.bat           # Frontend startup script
│
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda (recommended) or virtual environment
- Azure OpenAI API key
- Tavily API key (optional, for enhanced web search)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/virat-kumar/course-gap-analyzer.git
   cd course-gap-analyzer
   ```

2. **Create and activate Conda environment**:
   ```bash
   conda create -n course-gap-analyzer python=3.10
   conda activate course-gap-analyzer
   ```

3. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

### Configuration

1. **Create backend environment file**:
   ```bash
   cd backend
   cp .env.example .env  # Or create .env manually
   ```

2. **Configure `.env` file**:
   ```env
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_MODEL=gpt-4o
   API_VERSION=2024-02-15-preview

   # Tavily API (Optional)
   TAVILY_API_KEY=your-tavily-api-key

   # Database (SQLite - defaults to syllabus_gap_analyzer.db)
   DATABASE_URL=sqlite:///./syllabus_gap_analyzer.db
   ```

### Running the Application

#### Option 1: Using Batch Scripts (Windows)

1. **Start Backend**:
   ```bash
   cd backend
   start_backend.bat
   ```
   Backend will run on `http://localhost:8000`

2. **Start Frontend**:
   ```bash
   cd frontend
   start_frontend.bat
   ```
   Frontend will run on `http://localhost:8501`

#### Option 2: Manual Start

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   conda activate course-gap-analyzer
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   conda activate course-gap-analyzer
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

3. **Access the Application**:
   - Frontend UI: http://localhost:8501
   - Backend API Docs: http://localhost:8000/docs
   - Backend Health: http://localhost:8000/health

## 📖 Usage Guide

### Method 1: Using the Chat Interface (Recommended)

1. **Upload PDF**:
   - Go to the "Chat" tab
   - Click "📄 Upload PDF here" at the top
   - Select your syllabus PDF file
   - Click "Upload"
   - The system will extract topics automatically

2. **Search for Jobs**:
   - In the chat, type: "Search for data engineering jobs from top tech companies"
   - The system will automatically search and collect job descriptions

3. **Request Analysis**:
   - Type: "Analyze the gaps between my syllabus and those job requirements"
   - The system will generate Table A and Table B with detailed analysis

4. **Ask Questions**:
   - Continue the conversation to ask about specific topics
   - Example: "What are the top 3 missing topics I should prioritize?"

### Method 2: Using Dedicated Tabs

1. **Upload PDF Tab**:
   - Upload your syllabus PDF
   - View extracted topics and text preview

2. **Search Jobs Tab**:
   - Enter search criteria (e.g., "Find Data Engineer jobs from top companies in the last 30 days")
   - Click "Search Jobs"
   - View search results

3. **Analyze Gaps Tab**:
   - Click "Analyze Gaps" button
   - View Table A (Viable Topics) and Table B (Missing Topics)
   - Each table includes relevance scores, priorities, and reference URLs

## 🔌 API Endpoints

### Backend API Documentation

Full interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

### Main Endpoints

#### 1. `POST /pdf`
Upload and process a syllabus PDF.

**Request**: Multipart form data with PDF file

**Response**:
```json
{
  "document_id": "uuid",
  "extracted_text_preview": "first 500 characters...",
  "topic_extract_status": "completed"
}
```

#### 2. `POST /search`
Search for job descriptions based on constraints.

**Request**:
```json
{
  "conversation_id": "uuid (optional)",
  "instruction": "Find data engineering jobs from top companies"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "parsed_constraints": {...},
  "verified": true,
  "results_count": 120,
  "sources_sample": [...]
}
```

#### 3. `POST /analyze`
Generate gap analysis comparing syllabus with job requirements.

**Request**:
```json
{
  "conversation_id": "uuid",
  "document_id": "uuid"
}
```

**Response**:
```json
{
  "table_a": [
    {
      "syllabus_topic": "SQL Queries",
      "industry_relevance_score": 95,
      "evidence_job_count": 45,
      "example_industry_phrasing": "Advanced SQL queries",
      "notes": "Still highly relevant",
      "references": ["url1", "url2"]
    }
  ],
  "table_b": [
    {
      "missing_topic": "MLOps",
      "frequency_in_jobs": 28,
      "priority": "High",
      "suggested_syllabus_insertion": "Week 11",
      "rationale": "Emerging in industry",
      "references": ["url3", "url4"]
    }
  ]
}
```

#### 4. `POST /chat`
Natural language chat interface with automatic tool calling.

**Request**:
```json
{
  "message": "Search for data engineering jobs",
  "conversation_id": "uuid (optional)",
  "document_id": "uuid (optional)"
}
```

**Response**:
```json
{
  "response": "I found 120 job descriptions...",
  "conversation_id": "uuid",
  "document_id": "uuid",
  "tool_calls": [{"tool": "search", "status": "completed"}],
  "tables": {...}  // If analysis was performed
}
```

#### 5. `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## 🗄️ Database Schema

The application uses SQLite with the following main tables:

- **`documents`**: Stores uploaded PDF documents
- **`syllabus_topics`**: Extracted topics from syllabi
- **`conversations`**: Conversation sessions
- **`chat_messages`**: Chat message history for multi-turn conversations
- **`job_sources`**: Job posting sources and URLs
- **`job_topics`**: Topics extracted from job descriptions
- **`analysis_runs`**: Analysis execution records
- **`analysis_table_a_rows`**: Table A results (viable topics)
- **`analysis_table_b_rows`**: Table B results (missing topics)

Database file: `backend/syllabus_gap_analyzer.db` (created automatically)

## 🧪 Testing

### Running Tests

The project includes comprehensive test scripts:

```bash
cd backend
conda activate course-gap-analyzer

# Test UI conversation flow
python test_ui_conversation_flow.py

# Test chat interface
python test_chat_interface_full_flow.py

# Test PDF upload flow
python test_chat_pdf_upload_flow.py
```

### Manual Testing

1. **Test PDF Upload**: Use the test PDF in `backend/test_data/`
2. **Test Chat Interface**: Use natural language to interact
3. **Test Analysis**: Upload PDF → Search Jobs → Analyze Gaps

## 🔒 Security Features

- **Input Sanitization**: All external content (PDFs, web pages) is sanitized to prevent prompt injection
- **Security Guardrails**: LLM prompts include security rules to ignore malicious instructions
- **CORS Configuration**: Configurable CORS for production deployments
- **Environment Variables**: Sensitive keys stored in `.env` (not in git)

## 🛠️ Development

### Code Structure

- **Separation of Concerns**: Clear separation between API routes, services, and data access
- **Repository Pattern**: Data access abstracted through repository classes
- **Service Layer**: Business logic in service classes
- **Schema Validation**: Pydantic schemas for request/response validation
- **Prompt Management**: All LLM prompts centralized in `prompts/prompts.py`

### Adding New Features

1. **New API Endpoint**: Add route in `app/api/`
2. **New Service**: Add service class in `app/services/`
3. **New Database Model**: Add model in `app/db/models.py`
4. **New LLM Prompt**: Add to `prompts/prompts.py`

### Environment Configuration

Update `.env` file for different environments:
- Development: `localhost` URLs
- Production: Update CORS origins, database paths, etc.

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check if port 8000 is available
   - Verify `.env` file exists and has correct Azure OpenAI credentials
   - Ensure Conda environment is activated

2. **Frontend can't connect to backend**:
   - Verify backend is running on port 8000
   - Check `BACKEND_URL` in `frontend/app.py`
   - Ensure CORS is properly configured

3. **PDF upload fails**:
   - Check file size (large PDFs may take time)
   - Verify PDF is not corrupted
   - Check backend logs for errors

4. **Analysis returns empty tables**:
   - Ensure PDF has been uploaded
   - Ensure job search has been completed
   - Check database for stored data

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with FastAPI, LangChain, and Streamlit
- Uses Azure OpenAI for LLM capabilities
- Tavily API for web search functionality

---

**Note**: Make sure to keep your `.env` file secure and never commit it to version control. The `.gitignore` file is configured to exclude sensitive files.

