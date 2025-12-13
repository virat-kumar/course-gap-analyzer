# Backend Commands

## Step-by-Step Commands

### 1. Change Directory
```powershell
cd C:\Users\virat\OneDrive\Projects\course-gap-analyzer\backend
```

### 2. Activate Conda Environment
```powershell
conda activate course-gap-analyzer
```

### 3. Run Backend Server (on ALL interfaces - 0.0.0.0)
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

## Complete One-Liner (PowerShell)
```powershell
cd C:\Users\virat\OneDrive\Projects\course-gap-analyzer\backend; conda activate course-gap-analyzer; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

## Or Use the Batch File
Simply double-click:
```
backend\start_backend.bat
```

## Access URLs
- **Localhost**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Network**: http://192.168.10.150:8000 (or your machine's IP)


