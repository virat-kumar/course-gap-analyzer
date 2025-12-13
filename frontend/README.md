# Syllabus Gap Analyzer - Frontend

Streamlit frontend application for the Syllabus Gap Analyzer system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the backend server is running:
```bash
cd ../backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## Features

- **Upload PDF**: Upload and extract topics from syllabus PDF
- **Search Jobs**: Search for industry job descriptions
- **Analyze Gaps**: Generate gap analysis tables
- **Chat Interface**: Natural language interaction with the system


