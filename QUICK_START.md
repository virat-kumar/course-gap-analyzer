# Quick Start Guide

## Starting the Application

### Step 1: Start Backend (Terminal 1)

**IMPORTANT: Use `--host 0.0.0.0` for all network interfaces**

```bash
cd backend
conda activate course-gap-analyzer
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 2: Start Frontend (Terminal 2)

**IMPORTANT: Use `--server.address 0.0.0.0` for all network interfaces**

```bash
cd frontend
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://0.0.0.0:8501
```

## Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Using the Application

1. **Upload PDF** (Tab 1):
   - Click "Choose a PDF file"
   - Select your syllabus PDF
   - Click "Upload and Extract Topics"
   - Wait for topic extraction to complete

2. **Search Jobs** (Tab 2 or Chat Tab):
   - Enter search criteria (e.g., "Find Data Engineer jobs from top companies")
   - Wait for search to complete
   - View results

3. **Analyze Gaps** (Tab 3 or Chat Tab):
   - Click "Generate Analysis" or ask in chat
   - View Table A (viable topics) and Table B (missing topics)
   - Review references and recommendations

4. **Chat** (Tab 4):
   - Use natural language
   - Ask to search or analyze
   - View results in conversation

## Monitoring

Watch the terminal windows for logs:
- **Backend**: API requests, LLM calls, errors
- **Frontend**: User interactions, errors

## Troubleshooting

- **Port in use**: Check if another process is using ports 8000/8501
- **Cannot connect**: Verify servers are on 0.0.0.0 (not 127.0.0.1)
- **Import errors**: Activate conda environment first


