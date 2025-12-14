# Server Startup Notes

## IMPORTANT: Both Servers Run on ALL Network Interfaces (0.0.0.0)

Both the backend and frontend servers are configured to run on **0.0.0.0**, which means they are accessible from:
- Localhost: http://localhost:8000 (backend) and http://localhost:8501 (frontend)
- All network interfaces: http://0.0.0.0:8000 (backend) and http://0.0.0.0:8501 (frontend)
- Other devices on your network: http://<your-machine-ip>:8000 and http://<your-machine-ip>:8501

## Starting Servers

### Backend Server (Terminal 1)

```bash
cd backend
conda activate course-gap-analyzer
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

**Important**: 
- Uses `--host 0.0.0.0` to bind to all interfaces
- Uses `--reload` for auto-reload on code changes
- Uses `--log-level info` for detailed logging
- Logs will show in this terminal window

### Frontend Server (Terminal 2)

```bash
cd frontend
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

**Important**:
- Uses `--server.address 0.0.0.0` to bind to all interfaces
- Uses `--server.port 8501` for the frontend port
- Logs will show in this terminal window

## Monitoring Logs

### Backend Logs
- All API requests and responses
- Database operations
- LLM API calls
- Error messages and stack traces
- Uvicorn server logs

### Frontend Logs
- Streamlit app activity
- User interactions
- API call errors (if any)
- Streamlit server logs

## Testing

Run the comprehensive test:
```bash
cd frontend
python test_frontend_ui.py
```

This will test:
1. Backend health
2. Frontend accessibility
3. PDF upload
4. Topic extraction
5. Chat search
6. Gap analysis

## Access URLs

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Troubleshooting

If servers don't start:
1. Check if ports 8000 and 8501 are already in use
2. Ensure conda environment is activated
3. Check that all dependencies are installed
4. Verify .env file exists with correct credentials


