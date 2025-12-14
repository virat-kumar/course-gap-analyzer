# Starting Backend and Frontend Servers

## ⚠️ IMPORTANT: Both servers MUST run on ALL network interfaces (0.0.0.0)

This allows access from:
- Localhost
- Other devices on your network
- All network interfaces

## Backend Server (Terminal 1)

**IMPORTANT: Must use `--host 0.0.0.0` to bind to all interfaces**

```bash
cd backend
conda activate course-gap-analyzer
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

**Key parameters:**
- `--host 0.0.0.0` - Binds to ALL network interfaces (required!)
- `--port 8000` - Backend port
- `--reload` - Auto-reload on code changes
- `--log-level info` - Detailed logging

**Access:**
- http://localhost:8000
- http://0.0.0.0:8000
- http://<your-ip>:8000 (from network)

## Frontend Server (Terminal 2)

**IMPORTANT: Must use `--server.address 0.0.0.0` to bind to all interfaces**

```bash
cd frontend
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

**Key parameters:**
- `--server.address 0.0.0.0` - Binds to ALL network interfaces (required!)
- `--server.port 8501` - Frontend port

**Access:**
- http://localhost:8501
- http://0.0.0.0:8501
- http://<your-ip>:8501 (from network)

## Verifying Servers are Running

### Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Check Frontend
```bash
curl http://localhost:8501
# Should return HTML (status 200)
```

## Monitoring Logs

Both servers display logs in their terminal windows:

**Backend logs show:**
- Server startup
- API requests (GET, POST, etc.)
- Request paths and status codes
- LLM API calls
- Database operations
- Errors and stack traces

**Frontend logs show:**
- Streamlit startup
- User interactions
- API call errors (if any)
- App activity

## Network Access

If your machine's IP is `192.168.10.150`:
- Frontend: http://192.168.10.150:8501
- Backend: http://192.168.10.150:8000

## Troubleshooting

1. **Port already in use**: Stop existing processes, check ports
2. **Cannot connect**: Verify servers are running on 0.0.0.0 (not 127.0.0.1)
3. **Import errors**: Ensure conda environment is activated
4. **Missing modules**: Run `pip install -r requirements.txt` in backend folder
