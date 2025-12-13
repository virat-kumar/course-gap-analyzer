# Frontend Commands

## Step-by-Step Commands

### 1. Change Directory
```powershell
cd C:\Users\virat\OneDrive\Projects\course-gap-analyzer\frontend
```

### 2. Activate Conda Environment
```powershell
conda activate course-gap-analyzer
```

### 3. Run Frontend Server (on ALL interfaces - 0.0.0.0)
```powershell
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Complete One-Liner (PowerShell)
```powershell
cd C:\Users\virat\OneDrive\Projects\course-gap-analyzer\frontend; conda activate course-gap-analyzer; streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Or Use the Batch File
Simply double-click:
```
frontend\start_frontend.bat
```

## Access URLs
- **Localhost**: http://localhost:8501
- **Network**: http://192.168.10.150:8501 (or your machine's IP)


